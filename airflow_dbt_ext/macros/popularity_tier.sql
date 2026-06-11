{% macro popularity_tier(column_name) %}
    case
        when {{ column_name }} >= 100 then 'high'
        when {{ column_name }} >= 20  then 'medium'
        else                               'low'
    end
{% endmacro %}
