from django import template

register = template.Library()

@register.filter(name='alert_class')
def alert_class(level: int) -> str:
    alert_classes = {
        40: "danger",
        25: "success",
    }
    return alert_classes.get(level, "primary") 
