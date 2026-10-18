"""Check actual JS descriptors against the existing Draft2020 source contract.

Optional test-only validator; never installed or required by the product.
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None


@unittest.skipUnless(
    jsonschema and shutil.which("node"),
    "Existing jsonschema and Node test tools required",
)
class Descriptor(unittest.TestCase):
    def test_actual_descriptors_are_valid_but_stale_is_not_ready_for_handoff(self):
        root = Path(__file__).resolve().parents[1]
        source = r"""
import {createStore} from './src/core/store.js';
import {describeDesign} from './src/core/design.js';
const store=createStore();store.dispatch({type:'create'});
const design={version:1,source:{artifact_sha256:'a'.repeat(64),media_type:'text/html',source_commit:null,reference_viewport:{width:1000,height:640}},preview:{artifact_sha256:'b'.repeat(64),media_type:'image/png',rendering_mode:'inert-image'},catalog:[{element_id:'id:button',tag:'button',count:1,resolution:'unique'}],bindings:{}};
store.dispatch({type:'designImport',design,expected_revision:store.getState().revision});
store.dispatch({type:'designBind',id:store.getState().boxes[0].id,operation:'move',element_id:'id:button',source_hash:design.source.artifact_sha256,expected_revision:store.getState().revision});
const positive=describeDesign(store.getState(),'synthetic-project','synthetic-snapshot','Move button');
const changed=structuredClone(design);changed.source.artifact_sha256='c'.repeat(64);
store.dispatch({type:'designImport',design:changed,expected_revision:store.getState().revision});
console.log(JSON.stringify([positive,describeDesign(store.getState(),'synthetic-project','synthetic-snapshot','Move button')]));
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", source],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        positive, stale = json.loads(result.stdout)
        schema = json.loads(
            (root / "docs/contracts/design-source-v1.schema.json").read_text()
        )
        validator = jsonschema.Draft202012Validator(schema)
        for value in [positive, stale]:
            validator.validate(value["descriptor"])
            self.assertFalse(value["execution_ready"])
            self.assertFalse(value["execution_started"])
        self.assertTrue(positive["ready"])
        self.assertFalse(stale["ready"])
        self.assertEqual(
            stale["descriptor"]["elements"][0]["source_element"]["resolution"],
            "unresolved",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
