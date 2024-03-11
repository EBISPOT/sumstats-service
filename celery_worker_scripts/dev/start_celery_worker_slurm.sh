#!/bin/bash

ENV_FILE="/hps/software/users/parkinso/spot/gwas/dev/scripts/cron/sumstats_service/cel_envs_sandbox"
LOG_LEVEL="info"
MEM="8000"
CLUSTER_QUEUE="standard"

source $ENV_FILE

# Module install cmd
lmod_cmd="module load singularity-3.6.4-gcc-9.3.0-yvkwp5n; module load openjdk-16.0.2-gcc-9.3.0-xyn6nf5; module load nextflow-21.10.6-gcc-9.3.0-tkuemwd"

# Set Singularity cmd
singularity_cmd="singularity exec --env-file $ENV_FILE --bind /usr/lib64/libmunge.so.2:/usr/lib/x86_64-linux-gnu/libmunge.so.2 --bind /var/run/munge:/var/run/munge $SINGULARITY_CACHEDIR/gwas-sumstats-service_${SINGULARITY_TAG}.sif"

# Set celery worker cmd
# TODO: update scripts in lsf and slurm clusters
celery_cmd="celery -A sumstats_service.app.celery worker --loglevel=${LOG_LEVEL} --queues=${CELERY_QUEUE1},${CELERY_QUEUE2},${CELERY_QUEUE3} > celery_worker_slurm_dev.log 2>&1"

# Shutdown gracefully all jobs named sumstats_service_celery_worker
# --full is required because "By default, signals other than SIGKILL 
# are not sent to the batch step (the shell script). With this 
# option scancel also signals the batch script and its children processes."
# See https://slurm.schedmd.com/scancel.html#OPT_full
echo "sending SIGTERM signal to dev celery workers"
scancel --name=sumstats_service_celery_worker --signal=TERM --full

# Submit new SLURM jobs for celery workers
echo "START spinning up dev celery workers:"
for WORKER_ID in {1..2}; do
    echo $WORKER_ID
    sbatch --parsable --output="cel_slurm_dev_${WORKER_ID}.o" --error="cel_slurm_dev_${WORKER_ID}.e" --mem=${MEM} --time=7-00:00:00 --job-name=sumstats_service_celery_worker --wrap="${lmod_cmd}; ${singularity_cmd} ${celery_cmd}"
done
echo "DONE spinning up dev celery workers"

