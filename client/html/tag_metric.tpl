<div class='tag-metric'>
    <form class='horizontal edit-metric'>
        <%= ctx.makeNumericInput({
            text: 'Minimum',
            name: 'metric-min',
            value: ctx.metricMin,
            enabled: ctx.canEditMetricBounds,
        }) %>
        <%= ctx.makeNumericInput({
            text: 'Maximum',
            name: 'metric-max',
            value: ctx.metricMax,
            enabled: ctx.canEditMetricBounds,
        }) %>

        <div class='buttons'>
            <% if (!ctx.tag.metric && ctx.canCreateMetric) { %>
                <input type='submit' >Create metric</input>
            <% } else if (ctx.tag.metric && ctx.canEditMetricBounds) { %>
                <input type='submit' >Update metric</input>
            <% } %>
        </div>
    </form>
</div>