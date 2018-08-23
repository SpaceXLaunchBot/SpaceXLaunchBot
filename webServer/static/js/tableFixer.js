function fixTable() {
    /*
    Determines height for table so that it fits the viewport correctly
    */
    let titleHeight = $("#tableTitle").outerHeight(true);
    let logTableHeadHeight = $("#logTableHead").outerHeight(true);
    // Log table should be viewport height - title height
    $("#logTable").height($(window).height() - titleHeight);
    // Table body does the same but takes the table header height into account
    $("#logTableBody").height($(window).height() - logTableHeadHeight - titleHeight);

    /*
    Scrolls table all the way to the bottom
    */
    var logTableBody = document.getElementById("logTableBody");
    logTableBody.scrollTop = logTableBody.scrollHeight;
}

// Make sure this happens when the window size is changed as well
window.onresize = function(event) {
    fixTable();
};
