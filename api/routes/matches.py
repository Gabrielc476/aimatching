"""
Match routes for the API.

This module defines the routes for job-resume matching operations,
including match analysis and recommendations.
"""
from flask_restful import Api

from ..controllers.match_controller import (
    MatchAnalysisResource,
    MatchRecommendationsResource
)


def register_match_routes(api: Api):
    """Register match related routes.

    Args:
        api: Flask-RESTful API instance
    """
    api.add_resource(MatchAnalysisResource, '/match/analyze')
    api.add_resource(MatchRecommendationsResource, '/match/recommendations')