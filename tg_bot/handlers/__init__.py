from .start import router as r_start
from .how_to_start import router as r_how_to_start
from .order_feedbacks import router as r_order_feedbacks
from .active_orders import router as r_active_orders
from .ask_question import router as r_ask_question

routers = [r_start, r_how_to_start, r_order_feedbacks, r_active_orders, r_ask_question]
