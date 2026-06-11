{% macro yr_mos(column_name) %}
    concat(
        cast(floor({{ column_name }} / 12) as string),
        '/',
        cast(mod({{ column_name }}, 12) as string)
    )
{% endmacro %}
