# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import jmespath
from chart_utils.helm_template_generator import render_chart


class TestDagsPersistentVolumeClaim:
    """Tests DAGs PVC."""

    def test_should_not_generate_a_document_if_persistence_is_disabled(self):
        docs = render_chart(
            values={"dags": {"persistence": {"enabled": False}}},
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )

        assert len(docs) == 0

    def test_should_not_generate_a_document_when_using_an_existing_claim(self):
        docs = render_chart(
            values={"dags": {"persistence": {"enabled": True, "existingClaim": "test-claim"}}},
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )

        assert len(docs) == 0

    def test_should_generate_a_document_if_persistence_is_enabled_and_not_using_an_existing_claim(self):
        docs = render_chart(
            values={"dags": {"persistence": {"enabled": True, "existingClaim": None}}},
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )

        assert len(docs) == 1

    def test_should_set_pvc_details_correctly(self):
        docs = render_chart(
            values={
                "dags": {
                    "persistence": {
                        "enabled": True,
                        "size": "1G",
                        "existingClaim": None,
                        "storageClassName": "MyStorageClass",
                        "accessMode": "ReadWriteMany",
                    }
                }
            },
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )

        assert jmespath.search("spec", docs[0]) == {
            "accessModes": ["ReadWriteMany"],
            "resources": {"requests": {"storage": "1G"}},
            "storageClassName": "MyStorageClass",
        }

    def test_single_annotation(self):
        docs = render_chart(
            values={
                "dags": {
                    "persistence": {
                        "enabled": True,
                        "size": "1G",
                        "existingClaim": None,
                        "storageClassName": "MyStorageClass",
                        "accessMode": "ReadWriteMany",
                        "annotations": {"key": "value"},
                    }
                }
            },
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )

        annotations = jmespath.search("metadata.annotations", docs[0])
        assert annotations.get("key") == "value"

    def test_multiple_annotations(self):
        docs = render_chart(
            values={
                "dags": {
                    "persistence": {
                        "enabled": True,
                        "size": "1G",
                        "existingClaim": None,
                        "storageClassName": "MyStorageClass",
                        "accessMode": "ReadWriteMany",
                        "annotations": {"key": "value", "key-two": "value-two"},
                    }
                }
            },
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )

        annotations = jmespath.search("metadata.annotations", docs[0])
        assert annotations.get("key") == "value"
        assert annotations.get("key-two") == "value-two"

    def test_dags_persistent_volume_claim_template_storage_class_name(self):
        docs = render_chart(
            values={
                "dags": {
                    "persistence": {
                        "existingClaim": None,
                        "enabled": True,
                        "storageClassName": "{{ .Release.Name }}-storage-class",
                    }
                }
            },
            show_only=["templates/dags-persistent-volume-claim.yaml"],
        )
        assert jmespath.search("spec.storageClassName", docs[0]) == "release-name-storage-class"
