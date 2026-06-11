{% macro rating_bucket(column_name) %}
    case
        when {{ column_name }} >= 7.0 then 'well_rated'
        when {{ column_name }} >= 5.0 then 'average'
        else                          'low_rated'
    end
{% endmacro %}