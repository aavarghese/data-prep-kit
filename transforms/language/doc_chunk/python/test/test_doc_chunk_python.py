# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os

from data_processing.runtime.pure_python import PythonTransformLauncher
from data_processing.test_support.launch.transform_test import (
    AbstractTransformLauncherTest,
)
from doc_chunk_transform import (
    chunking_type_cli_param, 
    output_chunk_column_name_cli_param,
    chunking_types
)
from doc_chunk_transform_python import DocChunkPythonTransformConfiguration


class TestPythonDocChunkTransform(AbstractTransformLauncherTest):
    """
    Extends the super-class to define the test data for the tests defined there.
    The name of this class MUST begin with the word Test so that pytest recognizes it as a test class.
    """

    def get_test_transform_fixtures(self) -> list[tuple]:
        basedir = "../test-data"
        basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), basedir))
        fixtures = []
        launcher = PythonTransformLauncher(DocChunkPythonTransformConfiguration())

        # Run with JSON Chunker
        fixtures.append(
            (
                launcher,
                {
                    chunking_type_cli_param: chunking_types.DL_JSON,
                },
                basedir + "/input",
                basedir + "/expected",
            )
        )

        # Run with Markdown chunker
        fixtures.append(
            (
                launcher,
                {
                    chunking_type_cli_param: chunking_types.LI_MARKDOWN,
                },
                basedir + "/input_md",
                basedir + "/expected_md",
            )
        )

        # Run with fixed size token chunker
        fixtures.append(
            (
                launcher,
                {
                    chunking_type_cli_param: chunking_types.LI_TOKEN_TEXT,
                    output_chunk_column_name_cli_param: "chunk_text"
                },
                basedir + "/input_token_text",
                basedir + "/expected_token_text",
            )
        )
        return fixtures
