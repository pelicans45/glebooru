<div class='tag-metric'>
    <form class='horizontal edit-metric'>
        <div class='metric-bounds-edit'>
            <%= ctx.makeNumericInput({
                text: 'Minimum',
                name: 'metric-min',
                value: ctx.metricMin,
                step: 'any',
                readonly: !ctx.canEditMetricBounds,
            }) %>
            <%= ctx.makeNumericInput({
                text: 'Maximum',
                name: 'metric-max',
                value: ctx.metricMax,
                step: 'any',
                readonly: !ctx.canEditMetricBounds,
            }) %>
        </div>

        <div class='buttons'>
            <% if (!ctx.tag.metric && ctx.canCreateMetric) { %>
                <input type='submit' value='Create metric'/>
            <% } else if (ctx.tag.metric && ctx.canEditMetricBounds) { %>
                <input type='submit' value='Update metric'/>
            <% } %>
        </div>
    </form>
</div>
