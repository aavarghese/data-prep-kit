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

from typing import Any
from argparse import ArgumentParser
from ray.actor import ActorHandle
from argparse import Namespace
from data_processing.data_access import DataAccessFactoryBase
from data_processing_ray.runtime.ray.runtime_configuration import (
    RayTransformRuntimeConfiguration,
)
from data_processing_ray.runtime.ray import (
    DefaultRayTransformRuntime,
    RayTransformLauncher,
)
from fdedup.transforms.base import (FdedupFilterTransformBase,
                                    FdedupFilterTransformConfigurationBase,
                                    doc_id_snapshot_directory_key, filter_cli_prefix,
                                    doc_id_cache_key,
                                    )
from fdedup_ray.transforms import doc_id_cpu_key, num_doc_id_key


filter_docid_cpu_cli_param = f"{filter_cli_prefix}{doc_id_cpu_key}"
filter_num_docid_cli_param = f"{filter_cli_prefix}{num_doc_id_key}"


class FdedupFilterTransformRay(FdedupFilterTransformBase):
    """
    Fdedup filter Python version
    """
    def __init__(self, config: dict[str, Any]):
        """
        Initialize based on the dictionary of configuration information.
        :param config: initialization parameters, with the following keys
        doc_column - name of doc column
        doc_id_int_column - name of int doc id column
        doc_id_cache - doc id cache
        """
        # superclass initialization
        super().__init__(config)

    def _get_unique_ids(self, ids: list[int]) -> dict[int, int]:
        """
        Get unique IDs
        :param ids: table ids
        :return: unique ids and clusters
        """
        from fdedup_ray.utils import FdedupSupportRay
        return FdedupSupportRay.get_unique_ids(actors=self.doc_id_cache, ids=ids)


class FdedupFilterRuntimeRay(DefaultRayTransformRuntime):
    """
    fuzzy dedup filter runtime support
    """

    def __init__(self, params: dict[str, Any]):
        from data_processing.utils import get_logger
        self.logger = get_logger(__name__)
        super().__init__(params=params)
        self.doc_collector = None
        self.n_docid = params.get(num_doc_id_key, 1)
        self.docid_cpu = params.get(doc_id_cpu_key, .5)

    def get_transform_config(
            self, data_access_factory: DataAccessFactoryBase, statistics: ActorHandle, files: list[str]
    ) -> dict[str, Any]:
        """
        Get the dictionary of configuration that will be provided to the transform's initializer.
        This is the opportunity for this runtime to create a new set of configuration based on the
        config/params provided to this instance's initializer.  This may include the addition
        of new configuration data such as ray shared memory, new actors, etc., that might be needed and
        expected by the transform in its initializer and/or transform() methods.
        :param data_access_factory - data access factory class being used by the RayOrchestrator.
        :param statistics - reference to statistics actor
        :param files - list of files to process
        :return: dictionary of transform init params
        """
        from fdedup_ray.utils import FdedupSupportRay
        self.doc_collector = FdedupSupportRay.create_doc_id_current(
            data_access_factory=data_access_factory, n_actors=self.n_docid, actor_cpu=self.docid_cpu,
            directory=self.params.get(doc_id_snapshot_directory_key, None), statistics=statistics, logger=self.logger)
        return self.params | {doc_id_cache_key: self.doc_collector}

    def compute_execution_stats(self, stats: dict[str, Any]) -> dict[str, Any]:
        """
        Update/augment the given stats object with runtime-specific additions/modifications.
        :param stats: output of statistics as aggregated across all calls to all transforms.
        :return: job execution statistics.  These are generally reported as metadata by the Ray Orchestrator.
        """
        # compute and add additional statistics
        dedup_prst = 100 * (1.0 - stats.get("result_documents", 1) / stats.get("source_documents", 1))
        return {"de duplication %": dedup_prst} | stats


class FdedupFilterTransformConfigurationRay(FdedupFilterTransformConfigurationBase):
    """
    Provides support for configuring and using the associated Transform class include
    configuration with CLI args and combining of metadata.
    """

    def __init__(self):
        super().__init__(transform_class=FdedupFilterTransformRay)

    def add_input_params(self, parser: ArgumentParser) -> None:
        """
        Add Transform-specific arguments to the given  parser.
        """
        super().add_input_params(parser)
        parser.add_argument(
            f"--{filter_docid_cpu_cli_param}",
            type=float,
            default=0.5,
            help="number of CPUs per doc-id hash"
        )
        parser.add_argument(
            f"--{filter_num_docid_cli_param}",
            type=int,
            default=1,
            help="number of doc id caches to use"
        )

    def apply_input_params(self, args: Namespace) -> bool:
        super().apply_input_params(args=args)
        self.logger.info(f"fuzzy dedup filter params are {self.params}")
        return True


class FdedupFilterRayTransformRuntimeConfiguration(RayTransformRuntimeConfiguration):
    def __init__(self):
        super().__init__(
            transform_config=FdedupFilterTransformConfigurationRay(),
            runtime_class=FdedupFilterRuntimeRay,
        )


if __name__ == "__main__":
    launcher = RayTransformLauncher(FdedupFilterRayTransformRuntimeConfiguration())
    launcher.launch()