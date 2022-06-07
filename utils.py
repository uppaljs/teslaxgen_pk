"Experimental"

from homeassistant.helpers import template
from homeassistant.core import valid_entity_id
from homeassistant.exceptions import TemplateError
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE


def _all_states_available(entity_states):
    return all(
        state not in (STATE_UNAVAILABLE, STATE_UNKNOWN, None) for state in entity_states
    )


def init(hass):
    "Entry point function that adds helper functions"

    def _get_entity_states(*entity_ids):
        entity_states = [STATE_UNKNOWN for i in range(len(entity_ids))]

        for i, entity_id in enumerate(entity_ids):
            if valid_entity_id(entity_id):
                entity_states[i] = hass.states.get(entity_id)
            else:
                raise TemplateError(f"Invalid entity ID '{entity_id}'")  # type: ignore[arg-type]

        return entity_states

    def states_available(*entity_ids):
        entity_states = _get_entity_states(entity_ids)

        return _all_states_available(entity_states)

    def derive_state(derive_func, *entity_ids):
        calculated_state = STATE_UNKNOWN
        entity_states = _get_entity_states(entity_ids)

        if any(state == STATE_UNAVAILABLE for state in entity_states):
            calculated_state = STATE_UNAVAILABLE

        elif _all_states_available(entity_states):
            calculated_state = derive_func(*entity_states)

        return calculated_state

    tpl = template.Template("", hass)
    tpl._env.globals["states_available"] = states_available
