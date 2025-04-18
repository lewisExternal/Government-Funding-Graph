"""Shared configuration file and used for the storing environment variables related to the project."""

import os

DOCKER_RUNNING = os.environ.get("DOCKER_RUNNING", False)

NODE_SIZE_SCALE_FACTOR = 10

SAMPLE_QUESTIONS = [
    "What projects are related to [entity]",
    "What is the project with the most funding for [entity]",
    "What people are related to project [entity]",
]

if __name__ == "__main__":
    pass
