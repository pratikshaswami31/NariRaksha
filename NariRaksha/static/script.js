
// Active Navbar Script
const links = document.querySelectorAll("nav a");

links.forEach(link => {
    if (window.location.pathname === new URL(link.href).pathname) {
        link.classList.add("active");
    }
});

// 🚨 SOS ALERT
function activateSOS() {
    alert("🚨 SOS Alert Sent Successfully!");
}
window.onload = function () {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            document.getElementById("latitude").value = position.coords.latitude;
            document.getElementById("longitude").value = position.coords.longitude;
        });
    }
};
// 📍 LIVE LOCATION
function shareLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            let lat = position.coords.latitude;
            let lon = position.coords.longitude;

            alert("📍 Your Location:\nLatitude: " + lat + "\nLongitude: " + lon);
        }, function() {
            alert("Location access denied ❌");
        });
    } else {
        alert("Geolocation not supported ❌");
    }
}

// 📞 EMERGENCY CALL
function makeCall() {
    window.location.href = "tel:100";  // India police
}

// 🗺 SAFE ZONES
function showSafeZones() {
    window.open("https://www.google.com/maps/search/police+station+near+me");
}

// 🤖 AI ALERT
function aiAlert() {
    let safe = Math.random() > 0.5;

    if (safe) {
        alert("🤖 AI: You are in a SAFE area ✅");
    } else {
        alert("⚠️ AI: Warning! Be cautious in this area!");
    }
}

// 👥 COMMUNITY
function openCommunity() {
    window.location.href = "/contact";  // you can change later
}

// mergency alert for index
function sendSOS() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function success(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Send data to backend
    fetch('/send_sos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        })
    })
    .then(response => response.json())
    .then(data => {
        alert("🚨 SOS Alert Sent Successfully!");
    });
}

function error() {
    alert("Unable to get your location.");
}

// valid email 
function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

const email = document.getElementById("email").value;

if (!validateEmail(email)) {
    alert("Please enter a valid email address");
}