document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const sections = document.querySelectorAll('.table-section');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));

            
            tab.classList.add('active');
            const target = tab.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });

    
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

    document.getElementById("table-id-input").value = tableId;  


    if (tableStatus === "available") {
        document.getElementById("booking-form").style.display = "block";
    } else {
        document.getElementById("booking-form").style.display = "none";
    }
}
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}
