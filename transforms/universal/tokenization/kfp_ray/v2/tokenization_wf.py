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

import kfp.compiler as compiler
import kfp.components as comp
import kfp.dsl as dsl
from kfp_support.workflow_support.runtime_utils import (
    ONE_HOUR_SEC,
    ONE_WEEK_SEC,
    ComponentUtils,
)


# the name of the job script
EXEC_SCRIPT_NAME: str = "tokenization_transform.py"

task_image = "quay.io/dataprep1/data-prep-kit/tokenization:0.2.0"

# components
base_kfp_image = "quay.io/dataprep1/data-prep-kit/kfp-data-processing:0.1.0"
# compute execution parameters. Use default one for now.
compute_exec_params_op = comp.func_to_container_op(
    func=ComponentUtils.default_compute_execution_params, base_image=base_kfp_image
)
# create Ray cluster
create_ray_op = comp.load_component_from_file("../../../kfp_ray_components/createRayComponent.yaml")
# execute job
execute_ray_jobs_op = comp.load_component_from_file("../../../kfp_ray_components/executeRayJobComponent.yaml")
# clean up Ray
cleanup_ray_op = comp.load_component_from_file("../../../kfp_ray_components/cleanupRayComponent.yaml")
# Task name is part of the pipeline name, the ray cluster name and the job name in DMF.
TASK_NAME: str = "tokenization"


@dsl.pipeline(
    name=TASK_NAME + "-ray-pipeline",
    description="Pipeline for tokenization",
)
def tokenization(
    # Ray cluster
    ray_name: str = "tkn-kfp-ray",  # name of Ray cluster
    ray_head_options: str = '{"cpu": 1, "memory": 4, "image_pull_secret": "", "image": "' + task_image + '" }',
    ray_worker_options: str = '{"replicas": 2, "max_replicas": 2, "min_replicas": 2, "cpu": 2, "memory": 4, '
    '"image_pull_secret": "", "image": "' + task_image + '"}',
    server_url: str = "http://kuberay-apiserver-service.kuberay.svc.cluster.local:8888",
    # data access
    data_s3_config: str = "{'input_folder': 'test/tokenization/ds01/input/', 'output_folder': 'test/tokenization/ds01/output/'}",
    data_s3_access_secret: str = "s3-secret",
    data_max_files: int = -1,
    data_num_samples: int = -1,
    # orchestrator
    runtime_actor_options: str = "{'num_cpus': 0.8}",
    runtime_pipeline_id: str = "pipeline_id",
    runtime_code_location: str = "{'github': 'github', 'commit_hash': '12345', 'path': 'path'}",
    # tokenizer parameters
    tkn_tokenizer: str = "hf-internal-testing/llama-tokenizer",
    tkn_doc_id_column: str = "document_id",
    tkn_doc_content_column: str = "contents",
    tkn_text_lang: str = "en",
    tkn_tokenizer_args: str = "cache_dir=/tmp/hf",
    tkn_chunk_size: int = 0,
    # additional parameters
    additional_params: str = '{"wait_interval": 2, "wait_cluster_ready_tmout": 400, "wait_cluster_up_tmout": 300, "wait_job_ready_tmout": 400, "wait_print_tmout": 30, "http_retries": 5}',
):
    """
    Pipeline to execute tokenization transform
    :param ray_name: name of the Ray cluster
    :param ray_head_options: head node options, containing the following:
        cpu - number of cpus
        memory - memory
        image - image to use
        image_pull_secret - image pull secret
    :param ray_worker_options: worker node options (we here are using only 1 worker pool), containing the following:
        replicas - number of replicas to create
        max_replicas - max number of replicas
        min_replicas - min number of replicas
        cpu - number of cpus
        memory - memory
        image - image to use
        image_pull_secret - image pull secret
    :param server_url - server url
    :param additional_params: additional (support) parameters, containing the following:
        wait_interval - wait interval for API server, sec
        wait_cluster_ready_tmout - time to wait for cluster ready, sec
        wait_cluster_up_tmout - time to wait for cluster up, sec
        wait_job_ready_tmout - time to wait for job ready, sec
        wait_print_tmout - time between prints, sec
        http_retries - http retries for API server calls
    :param data_s3_access_secret - s3 access secret
    :param data_s3_config - s3 configuration
    :param data_max_files - max files to process
    :param data_num_samples - num samples to process
    :param runtime_actor_options - actor options
    :param runtime_pipeline_id - pipeline id
    :param runtime_code_location - code location
    :param tkn_tokenizer - Tokenizer used for tokenization
    :param tkn_tokenizer_args - Arguments for tokenizer.
    :param tkn_doc_id_column - Column contains document id which values should be unique across dataset
    :param tkn_doc_content_column - Column contains document content
    :param tkn_text_lang - Specify language used in the text content for better text splitting if needed
    :param tkn_chunk_size - Specify >0 value to tokenize each row/text in chunks of characters (rounded in words)
    :return: None
    """
    # create clean_up task
    clean_up_task = cleanup_ray_op(ray_name=ray_name, run_id=dsl.RUN_ID_PLACEHOLDER, server_url=server_url)
    ComponentUtils.add_settings_to_component(clean_up_task, 60)
    # pipeline definition
    with dsl.ExitHandler(clean_up_task):
        # compute execution params
        compute_exec_params = compute_exec_params_op(
            worker_options=ray_worker_options,
            actor_options=runtime_actor_options,
        )
        ComponentUtils.add_settings_to_component(compute_exec_params, ONE_HOUR_SEC * 2)
        ComponentUtils.set_s3_env_vars_to_component(compute_exec_params, data_s3_access_secret)

        # start Ray cluster
        ray_cluster = create_ray_op(
            ray_name=ray_name,
            run_id=dsl.RUN_ID_PLACEHOLDER,
            ray_head_options=ray_head_options,
            ray_worker_options=ray_worker_options,
            server_url=server_url,
            additional_params=additional_params,
        )
        ComponentUtils.add_settings_to_component(ray_cluster, ONE_HOUR_SEC * 2)
        ray_cluster.after(compute_exec_params)
        # Execute job
        execute_job = execute_ray_jobs_op(
            ray_name=ray_name,
            run_id=dsl.RUN_ID_PLACEHOLDER,
            additional_params=additional_params,
            exec_params={
                "data_s3_config": data_s3_config,
                "data_max_files": data_max_files,
                "data_num_samples": data_num_samples,
                "runtime_num_workers": compute_exec_params.output,
                "runtime_worker_options": runtime_actor_options,
                "runtime_pipeline_id": runtime_pipeline_id,
                "runtime_job_id": dsl.RUN_ID_PLACEHOLDER,
                "runtime_code_location": runtime_code_location,
                "tkn_tokenizer": tkn_tokenizer,
                "tkn_tokenizer_args": tkn_tokenizer_args,
                "tkn_doc_id_column": tkn_doc_id_column,
                "tkn_doc_content_column": tkn_doc_content_column,
                "tkn_text_lang": tkn_text_lang,
                "tkn_chunk_size": tkn_chunk_size,
            },
            exec_script_name=EXEC_SCRIPT_NAME,
            server_url=server_url,
        )
        ComponentUtils.add_settings_to_component(execute_job, ONE_WEEK_SEC)
        ComponentUtils.set_s3_env_vars_to_component(execute_job, data_s3_access_secret)
        execute_job.after(ray_cluster)

    # Configure the pipeline level to one week (in seconds)
    dsl.get_pipeline_conf().set_timeout(ONE_WEEK_SEC)


if __name__ == "__main__":
    # Compiling the pipeline
    compiler.Compiler().compile(tokenization, __file__.replace(".py", ".yaml"))