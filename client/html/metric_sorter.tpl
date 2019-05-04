<div class='content-wrapper' id='metric-sorter'>
    <h2>Sorting metric "<%- ctx.primaryMetric %>"</h2>
    <form>
        <div class='posts-container'>
            <div class='left-post-container'></div>
            <div class='sorting-buttons'>
                <div class='compare-block'>
                    <button class='compare left-lt-right'>
                        <i class='fa fa-less-than'></i>
                    </button>
                    <button class='compare left-gt-right'>
                        <i class='fa fa-greater-than'></i>
                    </button>
                </div>
            </div>
            <div class='right-post-container'></div>
        </div>

        <div class='messages'></div>

        <div class='buttons'>
            <input class='mousetrap done-btn' type='submit' value='Done'>
            <a href class='mousetrap append skip-btn'>Skip</a>
        </div>
    </form>
</div>
