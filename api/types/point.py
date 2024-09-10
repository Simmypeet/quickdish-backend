from typing import Any

import sqlalchemy

from api.schemas.point import Point


class PointType(sqlalchemy.types.UserDefinedType[Any]):
    def get_col_spec(self) -> str:
        return "POINT"

    def bind_expression(
        self, bindvalue: sqlalchemy.BindParameter[Any]
    ) -> sqlalchemy.ColumnElement[Any] | None:
        return sqlalchemy.func.POINT(bindvalue)

    def bind_processor(self, dialect: sqlalchemy.Dialect) -> Any:
        def process(value: Point | tuple[float, float] | None) -> str | None:
            match value:
                case Point():
                    return f"({value.lat}, {value.lng})"
                case tuple():
                    return f"({value[0]}, {value[1]})"
                case None:
                    return None

        return process
