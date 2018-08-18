/*
 * Example of a row
<tr class="info">
    <td class="t-time">2018-08-15 08:09:35,339</td>
    <td class="t-level">INFO</td>
    <td class="t-route">modules.backgroundTasks.reaper</td>
    <td class="t-message">370270228342374403 is not a valid ID, removing from db </td>
</tr>`
*/

// Returns an array of arrays, each containing info for the 4 columns
let logApiUrl = "http://spacex-launch-bot.gq/api/log";

$.ajax({url:logApiUrl, success: function(result){
    $.each(result, function(index, item) {
        /*
        item[0] = timestamp
        item[1] = level
        item[2] = from
        item[3] = message
        */
       ("#logTableBody tr:last").after(
`<tr class=${item[1].toLowerCase()}>
<td class="t-time">${item[0]}</td>
<td class="t-level">${item[1]}</td>
<td class="t-route">${item[2]}</td>
<td class="t-message">${item[3]}</td>
</tr>`
        );
    });
}});
