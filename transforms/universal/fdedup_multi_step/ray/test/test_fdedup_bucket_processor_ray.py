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
import ast

from data_processing.test_support.launch.transform_test import (
    AbstractTransformLauncherTest,
)
from data_processing_ray.runtime.ray import RayTransformLauncher
from fdedup.transforms.base import (bucket_processor_num_permutations_cli_param,
                                    bucket_processor_threshold_cli_param,
                                    bucket_processor_minhash_snapshot_directory_cli_param,
                                    )
from fdedup_ray.transforms import (FdedupBucketProcessorRayTransformRuntimeConfiguration,
                                   bucket_processor_bucket_cpu_cli_param,
                                   bucket_processor_minhash_cpu_cli_param,
                                   bucket_processor_docid_cpu_cli_param,
                                   bucket_processor_processor_cpu_cli_param,
                                   bucket_processor_num_buckets_cli_param,
                                   bucket_processor_num_minhash_cli_param,
                                   bucket_processor_num_docid_cli_param,
                                   bucket_processor_num_processors_cli_param,
                                   )

class TestRayFdedupPreprocessorTransform(AbstractTransformLauncherTest):
    """
    Extends the super-class to define the test data for the tests defined there.
    The name of this class MUST begin with the word Test so that pytest recognizes it as a test class.
    """

    def get_test_transform_fixtures(self) -> list[tuple]:
        basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test-data"))
        launcher = RayTransformLauncher(FdedupBucketProcessorRayTransformRuntimeConfiguration())
        config = {"run_locally": True,
                  "data_files_to_use": ast.literal_eval("['']"),
                  bucket_processor_num_permutations_cli_param: 64,
                  bucket_processor_threshold_cli_param: .8,
                  bucket_processor_minhash_snapshot_directory_cli_param:
                      os.path.join(basedir, "input/snapshot/minhash"),
                  bucket_processor_bucket_cpu_cli_param: .5,
                  bucket_processor_minhash_cpu_cli_param: .5,
                  bucket_processor_docid_cpu_cli_param: .5,
                  bucket_processor_processor_cpu_cli_param: .8,
                  bucket_processor_num_buckets_cli_param: 1,
                  bucket_processor_num_minhash_cli_param: 1,
                  bucket_processor_num_docid_cli_param: 1,
                  bucket_processor_num_processors_cli_param: 2,
                  }
        return [(launcher, config, basedir + "/input/snapshot/buckets", basedir + "/bucket_processor")]

