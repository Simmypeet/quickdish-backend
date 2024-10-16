from api.state import State
from api.models.Tag import Tag as Tagmodel, RestaurantTag
from api.schemas.Tag import RestaurantTagCreate as RestaurantTagCreateSchema

async def create_tag(state: State, title: str ) -> int: 
    sql_tag = Tagmodel(
        title=title
    )
    state.session.add(sql_tag)
    state.session.flush()
    state.session.commit()
    
    return sql_tag.id

async def create_restaurant_tag(state: State, payload: RestaurantTagCreateSchema) -> int:
    sql_res_tag = RestaurantTag(
        tag_id = payload.tag_id,
        restaurant_id = payload.restaurant_id
    )
    state.session.add(sql_res_tag)
    state.session.flush()
    state.session.commit()
    
    return sql_res_tag.id
        