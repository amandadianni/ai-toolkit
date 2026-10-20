from __future__ import annotations

import pytest

from pipefy_sdk.graphql_problem import (
    GraphQLProblem,
    GraphQLProblemKind,
    classify_graphql_error_dicts,
)


@pytest.mark.parametrize(
    "code",
    [
        "FEATURE_BLOCKED",
        "FEATURE_NOT_ENABLED",
        "FEATURE_DISABLED",
        "FEATURE_UNAVAILABLE",
    ],
)
def test_feature_code_is_classified_as_feature_not_enabled(code: str) -> None:
    problem = classify_graphql_error_dicts(
        [{"message": "Feature unavailable", "extensions": {"code": code}}]
    )

    assert problem == GraphQLProblem(
        kind=GraphQLProblemKind.FEATURE_NOT_ENABLED,
        message="Feature unavailable",
        code=code,
    )


def test_padded_lowercase_feature_blocked_is_classified_with_code_verbatim() -> None:
    problem = classify_graphql_error_dicts(
        [
            {
                "message": "Feature unavailable",
                "extensions": {"code": " feature_blocked "},
            }
        ]
    )

    assert problem == GraphQLProblem(
        kind=GraphQLProblemKind.FEATURE_NOT_ENABLED,
        message="Feature unavailable",
        code=" feature_blocked ",
    )


def test_unrecognized_code_without_not_found_phrase_is_runtime() -> None:
    problem = classify_graphql_error_dicts(
        [{"message": "Something broke", "extensions": {"code": "SOMETHING_ELSE"}}]
    )

    assert problem == GraphQLProblem(
        kind=GraphQLProblemKind.RUNTIME,
        message="Something broke",
        code="SOMETHING_ELSE",
    )
