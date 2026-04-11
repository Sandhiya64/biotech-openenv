from openenv.core.env_server.http_server import create_fastapi_app
from .environment import BiotechEnvironment

from src.envs.biotech_env.models import BiotechAction, BiotechObservation

app = create_fastapi_app(
    BiotechEnvironment,
    action_cls=BiotechAction,
    observation_cls=BiotechObservation
)