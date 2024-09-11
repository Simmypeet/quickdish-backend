from typing import Any

import sqlalchemy

from sqlalchemy.sql.type_api import (
    _ResultProcessorType,  # type: ignore
)

from api.schemas.point import Point


class PointType(sqlalchemy.types.UserDefinedType[Point]):
    cache_ok = True

    def get_col_spec(self) -> str:
        return "POINT"

    def bind_expression(
        self, bindvalue: sqlalchemy.BindParameter[Point]
    ) -> sqlalchemy.ColumnElement[Point] | None:
        return bindvalue

    def result_processor(
        self, dialect: sqlalchemy.Dialect, coltype: object
    ) -> _ResultProcessorType[Point] | None:
        def process(value: Any) -> Point:
            lat, lng = value[1:-1].split(",")
            lat = lat.strip()
            lng = lng.strip()
            return Point(lat=float(lat), lng=float(lng))

        return process

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
