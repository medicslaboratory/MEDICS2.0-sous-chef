# coding=utf-8
import os
from string import Template
import logging
import paramiko

import script.config as config
from script.file_transfers import get_ssh_client


def slurm_executor(
        hostname,
        slurm_cpu,
        slurm_memory,
        slurm_timeout,
        singularity,
        singularity_registry,
        data_in_link,
        data_out_link,
        cuda_required,
        slurm_user_name,
        my_app_platform,
        my_app_api_key,
        my_project_xyz__cluster_url,
        min_cuda_version=""
):
    data = {
        "timeout"             : f"{slurm_timeout}",
        "cpu"                 : f"{slurm_cpu}",
        "cuda_required"       : f"{cuda_required}",  # not used
        "min_cuda_version"    : f"{min_cuda_version}",  # not used
        "memory"              : f"{slurm_memory}",
        "singularity"         : f"{singularity}",
        "singularity_registry": f"{singularity_registry}",
        "data"                : f"{data_in_link}",
        "data_out"            : f"{data_out_link}",
        "slurm_user_name"     : f"{slurm_user_name}",
        "my_app_platform"    : f"{my_app_platform}",
        "my_app_api_key"     : f"{my_app_api_key}",
        "my_project_xyz__cluster_url" : f"{my_project_xyz__cluster_url}"

    }

    logging.log(logging.INFO, "Starting job executor ...")
    job_path_local = config.JOB_DIRECTORY_LOCAL + config.JOB_FILENAME_LOCAL
    job_path_remote = config.JOB_DIRECTORY_REMOTE + config.JOB_FILENAME_REMOTE
    logging.log(logging.INFO, "Generate template ...")

    # template selection
    if cuda_required:
        active_template = config.SLURM_GPU_TEMPLATE
    else:
        active_template = config.SLURM_TEMPLATE

    with open(active_template, "r") as file_template:
        src = Template(file_template.read())
        result = src.substitute(data)
        print(result)

    try:
        os.mkdir(config.JOB_DIRECTORY_LOCAL)
    except OSError as error:
        pass
    logging.log(logging.INFO, f"Writing file {job_path_local} ...")
    with open(job_path_local, "w") as job_file:
        job_file.write(result)

    # ssh connection with paramiko
    logging.log(logging.INFO, "Open SSH connexion ...")
    ssh_client = get_ssh_client()

    # transfer the job batch script
    sftp = ssh_client.open_sftp()
    sftp.put(job_path_local, job_path_remote)
    logging.log(logging.INFO, "Sending job files ...")

    # transfer all scripts: output path and folders need to exist
    for file in os.listdir(config.SCRIPT_LOCAL):
        print("sending: " + config.SCRIPT_LOCAL + file
              + "  to:" + config.SCRIPT_REMOTE + file)
        sftp = ssh_client.open_sftp()
        sftp.put(config.SCRIPT_LOCAL + file, config.SCRIPT_REMOTE + file)

    # file on win have \r\n and not unix \n compatible by default without dos2unix
    stdin, stdout, stderr = ssh_client.exec_command(
        f"dos2unix {config.JOB_DIRECTORY_REMOTE + config.JOB_FILENAME_REMOTE}"
    )

    # executing the job
    stdin, stdout, stderr = ssh_client.exec_command(
        f"sbatch {config.JOB_DIRECTORY_REMOTE + config.JOB_FILENAME_REMOTE}"
    )
    output = stdout.read()
    print(output)
    stdin.close()

    # Close the SSH connection
    ssh_client.close()

if __name__ == "__main__":
    my_project_xyz__url = "https://my_project_xyz_-route-ul-val-prj-xyz-dv01.apps.ul-pca-pr-ul01.ulaval.ca"
    # FROM LISTENER
    slurm_timeout = "01:00"
    slurm_cpu = "15"
    slurm_memory = "32G"
    singularity = "systematic_mc_comp:0.1.3.sif"
    data_in = f"{my_project_xyz__url}/blabla"
    data_out = ""
    hostname = "login.valeria.science"
    cuda_required = True
    min_cuda_version = "9"
    slurm_user_name = "my_username"
    my_app_platform = "https://my_app.science"
    my_app_api_key = ""
    my_project_xyz__cluster_url = my_project_xyz__url

    slurm_executor(
        hostname,
        slurm_cpu,
        slurm_memory,
        singularity,
        slurm_timeout,
        data_in,
        data_out,
        cuda_required,
        slurm_user_name,
        my_app_platform,
        my_app_api_key,
        my_project_xyz__cluster_url,
        min_cuda_version
    )
