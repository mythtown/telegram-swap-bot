from aiogram.fsm.state import State, StatesGroup


class AddChannelState(StatesGroup):
    waiting_for_forward_or_id = State()


class CreativeState(StatesGroup):
    channel_id = State()
    waiting_for_ad_content = State()
    waiting_for_button_text = State()
    waiting_for_gift_content = State()
    waiting_for_gift_title = State()


class BroadcastState(StatesGroup):
    channel_id = State()  # None means all channels
    waiting_for_message = State()
    confirming = State()


class AdminState(StatesGroup):
    waiting_for_vip_user = State()
    waiting_for_vip_days = State()
    waiting_for_whitelist_user = State()
    waiting_for_mandatory_channel = State()
    waiting_for_ref_target = State()
    waiting_for_ref_days = State()
