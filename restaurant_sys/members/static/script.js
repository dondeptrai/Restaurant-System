document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const sections = document.querySelectorAll('.table-section');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and sections
            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));

            // Add active class to the clicked tab and corresponding section
            tab.classList.add('active');
            const target = tab.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });

    // Set default active tab
    tabs[0].classList.add('active');
    sections[0].classList.add('active');
});

function showTableInfo(table) {
    document.getElementById("table-info").style.display = "block";
    
    var tableId = table.getAttribute("data-id");
    var tableStatus = table.getAttribute("data-status");
    var tableSeat = table.getAttribute("data-seat_num");
    var tableType = table.getAttribute("data-type");

    document.getElementById("table-id").textContent = tableId;
    document.getElementById("table-status").textContent = tableStatus;
    document.getElementById("table-seat").textContent = tableSeat;
    document.getElementById("table-type").textContent = tableType;

    if (tableStatus === "available") {
        document.getElementById("order-button").style.display = "block";
    } else {
        document.getElementById("order-button").style.display = "none";  
    }
}