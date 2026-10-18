"""Exact design/source correlation over existing Bridge tasks, never a queue.

Default host has no client/profile. Only a trusted operator embedding can supply
the fixed client and project paths; browser data cannot configure either.
"""

import asyncio
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat
from threading import Lock
from uuid import uuid4

from ai_adapter import require, reject_secrets
from design_source import MAX_HTML, MAX_PNG, png_size
from project_store import UUID, atomic, encoded


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(saved, instruction):
    state = saved['body']['state']
    require(saved['head'] == saved['snapshot']['id'], 'designStale')
    design = state.get('design')
    require(design and len(state['boxes']) <= 256, 'designNoSource')
    require(isinstance(instruction, str) and 0 < len(instruction.strip()) <= 1000,
            'emptyOrder')
    elements, issues = [], []
    for box in state['boxes']:
        binding = deepcopy(design['bindings'].get(box['id'],
                           {'action': 'new', 'source_element': None}))
        ref = binding['source_element']
        if ref:
            matches = [v for v in design['bindings'].values()
                       if v['source_element']
                       and v['source_element']['artifact_sha256'] == ref['artifact_sha256']
                       and v['source_element']['element_id'] == ref['element_id']]
            valid = (ref['artifact_sha256'] == design['source']['artifact_sha256']
                     and ref['resolution'] == 'unique' and len(matches) == 1
                     and any(v['element_id'] == ref['element_id']
                             and v['resolution'] == 'unique' and v['count'] == 1
                             for v in design['catalog']))
            if not valid:
                ref['resolution'] = 'unresolved'
                issues.append(box['id'])
        style = {k: box[k] for k in ['type', 'label', 'color', 'radius', 'font', 'layer']}
        require(len(encoded(style)) <= 4000, 'designElementLimit')
        elements.append({'box_id': box['id'], **binding,
                         'geometry': {k: box[k] for k in ['x', 'y', 'width', 'height']},
                         'requested_style': encoded(style).decode()})
    require(not issues, 'designUnresolved')
    value = {'format': 'blockdesigner.source.v1', 'project_id': saved['project_id'],
             'snapshot_id': saved['snapshot']['id'], 'document_revision': state['revision'],
             'document_size': state['document'], 'source': design['source'],
             'preview': design['preview'], 'view': {'zoom': state['ui']['zoom']},
             'elements': elements, 'requested_change': instruction}
    require(len(encoded(value)) <= 200000, 'contextTooLarge')
    reject_secrets(encoded(value).decode())
    return value


class FixedBridgeClient:
    """Existing optional KiraBridge SDK and operator-owned local configuration.

    No URL, token, principal or configuration path is accepted by HTTP handlers.
    An embedding owns this object; normal server startup does not instantiate it.
    """
    def __init__(self, config, principal):
        from kirabridge.local_runtime import peer
        self.peer = peer(config, principal)
        self.principal = principal

    async def call(self, name, arguments):
        from kirabridge.mcp_gateway.client import MCPClientPool
        async with MCPClientPool(max_connections=1, call_timeout=8) as pool:
            await pool.connect(self.peer)
            response = await pool.call(self.peer.id, name, arguments)
        value = response.structuredContent
        require(isinstance(value, dict) and value.get('error') is None, 'designBridgeUnknown')
        return value

    async def submit(self, value):
        return await self.call('task_request', {'request': value})

    async def task(self, identity):
        return await self.call('task_get', {'task_id': identity})


class DesignWorkflow:
    def __init__(self, projects, client=None, profiles=None):
        self.projects, self.client = projects, client
        self.profiles = dict(profiles or {})
        self.active = Lock()

    def folder(self, project):
        return self.projects.folder(project) / 'design-workflows'

    def load(self, project, identity):
        require(isinstance(identity, str) and UUID.fullmatch(identity), 'unknownTask')
        path = self.folder(project) / (identity + '.json')
        require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 2097152,
                'unknownTask')
        value = json.loads(path.read_bytes())
        require(value['project_id'] == project and value['id'] == identity, 'taskConflict')
        return value

    def save(self, value):
        raw = encoded(value)
        require(len(raw) <= 2097152, 'contextTooLarge')
        atomic(self.folder(value['project_id']) / (value['id'] + '.json'), raw)

    def public(self, value):
        return {k: deepcopy(v) for k, v in value.items()
                if k not in {'operations', 'issued', 'descriptor', 'files'}} | {
                    'client_available': self.client is not None
                    and value['project_id'] in self.profiles,
                    'project_completion_verified': False,
                    'source_commit_verified': False,
                    'automatic_retry': False,
                    'reply_verification': 'unverified',
                }

    def current(self, value):
        current = self.projects.read(value['project_id'])
        require(current['head'] == value['snapshot_id'], 'designStale')
        actual = descriptor(current, value['descriptor']['requested_change'])
        require(sha(encoded(actual)) == value['descriptor_sha256'], 'designStale')
        require(self.projects.raw(value['descriptor_sha256'], 200000) == encoded(actual),
                'designStale')
        return actual

    def prepare(self, project, snapshot, instruction):
        with self.projects.transaction():
            saved = self.projects.read(project, snapshot)
            value = descriptor(saved, instruction)
            digest = self.projects.raw_blob(encoded(value))
            folder = self.folder(project)
            paths = list(folder.glob('*.json'))
            for path in paths:
                prior = self.load(project, path.stem)
                if prior['descriptor_sha256'] == digest:
                    return self.public(prior)
            require(len(paths) < 64, 'designWorkflowLimit')
            record = {'id': str(uuid4()), 'project_id': project, 'snapshot_id': snapshot,
                      'document_revision': value['document_revision'], 'state': 'prepared',
                      'descriptor_sha256': digest, 'descriptor': value, 'operations': {},
                      'preview_sha256': value['preview']['artifact_sha256'],
                      'source_sha256': value['source']['artifact_sha256'],
                      'selection': deepcopy(saved['body']['state']['selection'])}
            self.save(record)
            return self.public(record)

    def fixed_file(self, profile, name, limit):
        root = Path(profile['cwd'])
        filename = profile[name]
        require(isinstance(filename, str) and filename and Path(filename).name == filename
                and filename not in {'.', '..'}, 'designProfileUnavailable')
        # Reuse the actual Bridge descriptor boundary when optional SDK is present.
        from kirabridge.filesystem_manager import PathScope
        with PathScope([str(root)]).parent(str(root / filename)) as (parent, leaf):
            fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            try:
                info = os.fstat(fd)
                require(stat.S_ISREG(info.st_mode) and info.st_size <= limit,
                        'designSourceLimit')
                with os.fdopen(fd, 'rb', closefd=False) as stream:
                    raw = stream.read(limit + 1)
                after = os.fstat(fd)
                require((info.st_size, info.st_mtime_ns, info.st_ctime_ns) ==
                        (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
                        and len(raw) == after.st_size, 'designStale')
                return raw
            finally:
                os.close(fd)

    async def operation(self, value, key, operation, arguments, wait=True):
        request_hash = sha(encoded([operation, arguments]))
        existing = value['operations'].get(key)
        if existing:
            require(existing['request_hash'] == request_hash, 'taskConflict')
            task = await self.client.task(existing['task_id'])
        else:
            require(len(value['operations']) < 128, 'designWorkflowLimit')
            task_id = 'bd_' + sha(encoded([value['project_id'], value['id'], key]))[:48]
            value['operations'][key] = {'task_id': task_id, 'request_hash': request_hash,
                                        'delivery': 'unknown_before_submit'}
            if key == 'start':
                value.update(bridge_task_id=task_id, state='unknown')
            # Durable identity BEFORE sending. On loss only task_get, never submit again.
            self.save(value)
            task = await self.client.submit({'task_id': task_id, 'idempotency_key': task_id,
                                            'operation': operation, 'arguments': arguments})
        require(task.get('id') == value['operations'][key]['task_id']
                and task.get('operation') == operation and task.get('args') == arguments
                and task.get('principal') == self.client.principal, 'taskConflict')
        if wait:
            for _ in range(40):
                if task['state'] not in {'queued', 'accepted', 'running'}:
                    break
                await asyncio.sleep(.05)
                task = await self.client.task(task['id'])
                require(task.get('id') == value['operations'][key]['task_id']
                        and task.get('operation') == operation and task.get('args') == arguments
                        and task.get('principal') == self.client.principal, 'taskConflict')
        value['operations'][key]['delivery'] = task['state']
        self.save(value)
        require(task.get('operation') == operation, 'taskConflict')
        if not wait:
            return task
        require(task['state'] == 'completed' and isinstance(task.get('result'), dict)
                and task['result'].get('success') is True, 'designBridgeUnknown')
        return task['result']['value']

    def issued(self, value, record):
        packet = record['handoff']
        require(record['content_hash'] == sha(encoded(packet))
                and packet['thread_id'] == value['thread_id']
                and packet['context']['notes'] == value['note'], 'taskConflict')
        refs = {item['reference']: item for item in record['source']['source_refs']}
        for digest in value['files']:
            path = str(self.projects.cas.root / digest)
            require(refs.get(path, {}).get('verification') == 'verified'
                    and refs[path].get('sha256') == digest, 'designSourceUnverified')
        return record

    async def action(self, project, identity, action, data=None):
        # Existing ProjectStore lock serializes callers/processes; no workers/startup replay.
        require(self.active.acquire(blocking=False), 'designBusy')
        try:
            return await self.locked_action(project, identity, action, data)
        finally:
            self.active.release()

    async def locked_action(self, project, identity, action, data):
        with self.projects.transaction():
            value = self.load(project, identity)
            require(self.client is not None and project in self.profiles,
                    'designProfileUnavailable')
            profile = self.profiles[project]
            self.current(value)
            try:
                async with asyncio.timeout(30):
                    await self.perform(value, profile, action, data or {})
            except Exception:
                value['last_error'] = 'designBridgeUnknown'
                self.save(value)
                raise
            value.pop('last_error', None)
            self.save(value)
            return self.public(value)

    async def perform(self, value, profile, action, data):
        require(action in {'issue', 'start', 'refresh', 'answer', 'decision'}, 'invalidAction')
        if action in {'issue', 'start', 'refresh'}:
            require(not data, 'invalidAction')
        self.current(value)
        if action == 'issue':
            require(not data, 'invalidAction')
            if 'issued' in value:
                self.issued(value, value['issued'])
                return
            require(sha(self.fixed_file(profile, 'source_file', MAX_HTML)) ==
                    value['source_sha256'], 'designStale')
            source = value['descriptor']['source']
            require(source['media_type'] == 'text/html', 'designNoSource')
            reject_secrets(self.projects.raw(value['source_sha256'], MAX_HTML).decode('utf-8'))
            created = await self.operation(value, 'create', 'threaddesk.manage', {
                'operation_id': 'create_' + value['id'], 'action': 'create',
                'expected_revision': 0, 'data': {'title': 'BlockDesigner ' + value['id']}})
            value['thread_id'] = created['thread_id']
            value['note'] = ('Explicit design request (untrusted context):\n'
                             + value['descriptor']['requested_change']
                             + '\nblockdesigner.source.v1 SHA256=' + value['descriptor_sha256']
                             + '\nExact project=' + value['project_id']
                             + ' snapshot=' + value['snapshot_id']
                             + ' revision=' + str(value['document_revision'])
                             + ' selected_box_ids=' + json.dumps(value['selection'])
                             + '\nOriginal source commit UNKNOWN; preview relation unverified.'
                             + '\nEdit the fixed source project, never mutate CAS references.'
                             + '\nReturn the changed source and inert PNG preview filenames: '
                             + profile['source_file'] + ', ' + profile['preview_file'])
            edited = await self.operation(value, 'note', 'threaddesk.manage', {
                'operation_id': 'note_' + value['id'], 'action': 'set_note',
                'id': value['thread_id'], 'expected_revision': created['revision'],
                'data': {'text': value['note']}})
            value['files'] = list(dict.fromkeys([value['descriptor_sha256'],
                                                value['source_sha256'], value['preview_sha256']]))
            for index, digest in enumerate(value['files']):
                edited = await self.operation(value, 'file_' + str(index), 'threaddesk.manage', {
                    'operation_id': 'file_' + str(index) + '_' + value['id'],
                    'action': 'add_file', 'id': value['thread_id'],
                    'expected_revision': edited['revision'],
                    'data': {'path': str(self.projects.cas.root / digest)}})
            record = await self.operation(value, 'issue', 'handoff.issue', {
                'operation_id': 'issue_' + value['id'], 'thread_id': value['thread_id'],
                'expected_revision': edited['revision'], 'target': 'codex'})
            value['issued'] = self.issued(value, record)
            value['handoff_id'] = record['handoff']['handoff_id']
            value['handoff_revision'] = record['handoff']['revision']
            value['state'] = 'issued_no_execution'
            return
        require('issued' in value, 'unknownTask')
        self.issued(value, value['issued'])
        reference = {'handoff_id': value['handoff_id'], 'revision': value['handoff_revision']}
        if action == 'start':
            require(not data, 'invalidAction')
            if 'start' not in value['operations']:
                for path in self.folder(value['project_id']).glob('*.json'):
                    previous = self.load(value['project_id'], path.stem)
                    require(previous['id'] == value['id'] or
                            'start' not in previous['operations'] or
                            previous.get('decision') in {'accepted', 'rejected', 'rework'},
                            'designBusy')
                require(sha(self.fixed_file(profile, 'source_file', MAX_HTML)) ==
                        value['source_sha256'], 'designStale')
            task = await self.operation(value, 'start', 'handoff.start', {
                **reference, 'cwd': str(profile['cwd']), 'agent': 'codex', 'timeout': 120.0},
                wait=False)
            value['state'] = task['state']
            value['bridge_task_id'] = task['id']
            value['bridge_receipt'] = task.get('receipt')
            return
        require('start' in value['operations'], 'unknownTask')
        if action == 'answer':
            require(set(data) == {'text'} and isinstance(data['text'], str)
                    and 0 < len(data['text'].strip()) <= 1000
                    and value['state'] == 'awaiting_answer', 'invalidAction')
            key = 'answer_' + value['question_id']
            task = await self.operation(value, key, 'handoff.answer', {
                **reference, 'question_id': value['question_id'],
                'answer_id': 'bd_' + sha(encoded([value['id'], value['question_id']]))[:48],
                'text': data['text'], 'timeout': 120.0}, wait=False)
            value['active_task_id'] = task['id']
            value['state'] = task['state']
            return
        active = await self.client.task(value.get('active_task_id') or value['bridge_task_id'])
        require(active['id'] == (value.get('active_task_id') or value['bridge_task_id'])
                and active['principal'] == self.client.principal, 'taskConflict')
        if active['state'] in {'created', 'queued', 'accepted', 'running', 'failed', 'blocked', 'cancelled'}:
            require(action == 'refresh', 'invalidAction')
            value['state'] = active['state']
            return
        poll = 'read_' + str(len(value['operations']))
        observed = await self.operation(value, poll, 'handoff.status', reference)
        require(observed['handoff_id'] == value['handoff_id']
                and observed['revision'] == value['handoff_revision']
                and observed['issued_content_hash'] == value['issued']['content_hash']
                and observed['first_task_id'] == value['bridge_task_id'], 'taskConflict')
        value['state'] = observed['phase']
        value['run_id'] = observed['run_id']
        value['session_id'] = observed['session_id']
        if observed['phase'] == 'awaiting_answer':
            task = await self.client.task(observed['last_task_id'])
            answer = task['result']['value']
            require(answer['question_id'] == observed['question_id'], 'taskConflict')
            value['question_id'] = observed['question_id']
            value['question'] = answer['question']
        if observed['phase'] not in {'delivered_unverified', 'accepted', 'rejected', 'rework'}:
            require(action == 'refresh', 'invalidAction')
            return
        inbox = await self.operation(value, poll + '_inbox', 'handoff.inbox',
                                     {'offset': 0, 'limit': 50})
        item = next((r for r in inbox['items'] if
                     r['return']['return_id'] == observed['return_id']), None)
        require(item is not None and item.get('binding_status') == 'issued_bound',
                'designReturnUnverified')
        reply = item['return']
        require(reply['handoff_id'] == value['handoff_id']
                and reply['handoff_revision'] == value['handoff_revision']
                and reply['run_id'] == value['run_id']
                and reply['task_id'] == observed['original_task_id']
                and reply['thread_id'] == value['thread_id']
                and reply['worker'] == 'codex', 'taskConflict')
        require({profile['source_file'], profile['preview_file']} <= set(reply['files']),
                'designReturnUnverified')
        original = self.fixed_file(profile, 'source_file', MAX_HTML)
        preview = self.fixed_file(profile, 'preview_file', MAX_PNG)
        png_size(preview)
        self.current(value)
        hashes = {'source_sha256': sha(original), 'preview_sha256': sha(preview)}
        if 'returned' in value:
            require(value['returned'] == hashes and value['return_id'] == reply['return_id'],
                    'taskConflict')
        self.projects.raw_blob(original)
        self.projects.raw_blob(preview)
        value['returned'], value['return_id'] = hashes, reply['return_id']
        value['summary'] = reply['result']
        if observed.get('decision'):
            value['decision'] = observed['decision']['choice']
        if action == 'decision':
            require(set(data) == {'choice', 'note'}
                    and data['choice'] in {'accepted', 'rejected', 'rework'}
                    and isinstance(data['note'], str) and 0 < len(data['note'].strip()) <= 1000,
                    'invalidAction')
            decision = await self.operation(value, 'decision', 'handoff.decide', {
                **reference, 'return_id': value['return_id'], **data})
            require(decision['return_id'] == value['return_id'], 'taskConflict')
            value['state'] = decision['phase']
            value['decision'] = data['choice']
        else:
            require(action == 'refresh' and not data, 'invalidAction')
