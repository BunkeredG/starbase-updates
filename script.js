// Dedicated Starship flight countdown
const starship_open = format("09/28/12/15");
const starship_close = format("09/28/13/30");
if (document.getElementById('starship')) {
    startCountdownFixed(starship_open, starship_close, 'starship');
}

// Date converter (MM/DD/HH/mm in UTC)
function format(date) {
    // [0] -> month | [1] -> day | [2] -> hour | [3] -> minute
    const dateL = date.split('/');
    return `2026-${dateL[0]}-${dateL[1]}T${dateL[2]}:${dateL[3]}:00Z`;
}

// Carousel setup
let show1 = true;
let carouselPick = 0;
const activeTimers = {};
let carouselData;

function checkForLaunchUpdates() {
    fetch('launches.json', {cache: 'no-store'}).then(response => response.json()).then(data => {
        carouselData = data;
        carousel(carouselData, "id1", "id2");
    });
}
checkForLaunchUpdates()
setInterval(checkForLaunchUpdates, 60000)

// Carousel logic
const carouselTimer = setInterval(() => carousel(carouselData, "id1", "id2"), 5000);

function carousel(data, id1, id2) {
    let current = data[carouselPick % data.length];
    if (show1) {
        document.getElementById(id1).classList.add('visible');
        document.getElementById(id2).classList.remove('visible');
        startCountdown(current[0], current[1], id1, current[2]);
    } else {
        document.getElementById(id2).classList.add('visible');
        document.getElementById(id1).classList.remove('visible');
        startCountdown(current[0], current[1], id2, current[2]);
    }

    show1 = !show1
    carouselPick++;
}

let closureData;

function checkForClosureUpdates() {
    fetch('closures.json', {cache: 'no-store'}).then(response => response.json()).then(data => {
        closureData = data;
        document.getElementById('closures').innerHTML = '';
        const [beachClosures, roadClosures] = closureData

        if (beachClosures[0] !== "No beach closures") {
            createBeachClosures(closureData[0]);
        }
        if (roadClosures[0] !== "No road closures") {
            createRoadClosures(closureData[1]);
        }
        if (beachClosures[0] === "No beach closures" && roadClosures[0] == "No road closures") {
            document.getElementById('closures').innerHTML = `<h3 class="launch">No planned closures</h3>`
        }
    });
}

if (document.getElementById('closures')) {
    checkForClosureUpdates()
    setInterval(checkForClosureUpdates, 60000)
}

function createRoadClosures(datalist) {
    for (const item of datalist) {
        const closureHTML = `
        <details>
        <summary class="dropdown-hover">Road Closure (${item[0]})</summary>
        <pre><b>DATE</b> - ${item[1]}</pre>
        </details>
        `
        document.getElementById('closures').insertAdjacentHTML('beforeend', closureHTML)
    }
}

function createBeachClosures(datalist) {
    for (const item of datalist) {
        const closureHTML = `
        <details>
        <summary class="dropdown-hover beach-closure">Beach Closure</summary>
        <pre><b>DATE</b> - ${item}</pre>
        </details>
        `
        document.getElementById('closures').insertAdjacentHTML('beforeend', closureHTML)
    }
}

// Hide notifications button for iOS users
function isIOS() {
    const ua = navigator.userAgent;
    const isAppleMobile = /iPhone|iPad/.test(ua);
    const isModernIPad = ua.includes('Mac') && navigator.maxTouchPoints > 1;
    return isAppleMobile || isModernIPad;
}

if (isIOS() && document.getElementById('permissions')) {
    document.getElementById('permissions').style.display = 'none';
}

// Scroll when opening <details>
document.querySelectorAll('details').forEach(function(details) {
  details.addEventListener('toggle', function() {
    if (details.open) {
      details.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }
  });
});

// Hash interaction
function openDetailsFromHash() {
    const hash = window.location.hash;
    if (!hash) return;

    const target = document.querySelector(hash);
    if (target && target.tagName === 'DETAILS') {
        target.open = true;
        target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

window.addEventListener('DOMContentLoaded', openDetailsFromHash);
window.addEventListener('hashchange', openDetailsFromHash);

// Notification permissions button
const permsButton = document.getElementById('permissions');
if (permsButton) {
    const initCheck = localStorage.getItem('subscribed') === 'true';
    permsButton.textContent = initCheck ? "Stop Receiving Updates" : "Get Updates";

    permsButton.addEventListener('click', function() {
        const isSubscribed = localStorage.getItem('subscribed') === 'true';

        if (isSubscribed) {
            localStorage.setItem('subscribed', 'false');
            new Notification('Unsubscribed!', {body: "You will no longer receive updates"});
            permsButton.textContent = "Get Updates";
        } else {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    fetch('notification.json', {cache: 'no-store'}).then(response => response.json()).then(data => {
                        localStorage.setItem('subscribed', 'true');
                        localStorage.setItem('lastSeenUpdate', data.id);
                        new Notification('Subscribed!', {body: "Leave this site open to get updates as soon as they're published"});
                        permsButton.textContent = "Stop Receiving Updates";
                    });
                }
            });
        }
    });
}

// Check for notification update
function checkForUpdate() {
    fetch('notification.json', {cache: 'no-store'}).then(response => response.json()).then(data => {
        const lastSeenID = localStorage.getItem('lastSeenUpdate');

        if (lastSeenID !== data.id) {
            if (localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                new Notification('Starbase Updates', {body: data.message});
            }
            localStorage.setItem('lastSeenUpdate', data.id);
        }
    });
}
checkForUpdate();
setInterval(checkForUpdate, 30000);

// Header fade
const fixedHeader = document.querySelector('.fixed-header');

function toggleFixedHeader() {
    if (window.scrollY > 100) {
        fixedHeader.classList.add('visible');
    } else {
        fixedHeader.classList.remove('visible');
    }
}

toggleFixedHeader();
window.addEventListener('scroll', toggleFixedHeader);

// Countdown to launch
function startCountdownFixed(openDate, closeDate, id) {
    const windowOpen = new Date(openDate);
    const windowClose = new Date(closeDate);
    let timer;

    function updateCountdown() {
        const now = new Date();
        const openDiff = windowOpen - now;
        const closeDiff = windowClose - now;
        let diff;

        if (closeDiff < 0) {
            document.getElementById(id).textContent = "(Window Closed)";
            document.getElementById(id).style.color = 'rgb(228, 17, 17)'
            clearInterval(timer);
            return;
        }

        if (openDiff < 0) {
            diff = closeDiff;
            document.getElementById(id).style.color = 'rgb(19, 159, 24)';
        }

        if (openDiff > 0) {
            diff = openDiff;
            document.getElementById(id).style.color = '';
        }

        const days = String(Math.floor(diff / (1000 * 60 * 60 * 24))).padStart(2, '0');
        const hours = String(Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
        const minutes = String(Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
        const seconds = String(Math.floor((diff % (1000 * 60)) / 1000)).padStart(2, '0');

        document.getElementById(id).textContent = `(${days}:${hours}:${minutes}:${seconds})`;
    }

    updateCountdown();
    timer = setInterval(updateCountdown, 1000);
}

// Countdown to launch in carousel
function startCountdown(openDate, closeDate, id, name) {
    if (activeTimers[id]) {
        clearInterval(activeTimers[id]);
    }

    const windowOpen = new Date(openDate);
    const windowClose = new Date(closeDate);
    const notifyKey = windowOpen.toISOString();

    function updateCountdown() {
        const now = new Date();
        const openDiff = windowOpen - now;
        const closeDiff = windowClose - now;
        let diff;

        if (closeDiff < 0) {
            if (localStorage.getItem('closeNotify-' + notifyKey) !== 'true' && localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                new Notification('Starbase Updates', {body: `Launch window for ${name} is closed`});
                localStorage.setItem('closeNotify-' + notifyKey, 'true');
            }

            document.getElementById(id).innerHTML = `${name}:<br><span class="countdown">(Window Closed)</span>`;
            document.querySelector(`#${id} .countdown`).style.color = 'rgb(228, 17, 17)';
            
            clearInterval(activeTimers[id]);
            return;

        } else if (openDiff < 0) {
            if (localStorage.getItem('openNotify-' + notifyKey) !== 'true' && localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                new Notification('Starbase Updates', {body: `Launch window for ${name} is open!`});
                localStorage.setItem('openNotify-' + notifyKey, 'true');
            }

            diff = closeDiff;
        } else {
            if (openDiff - (1000 * 60 * 10) < 0) {
                if (localStorage.getItem('10minNotify-' + notifyKey) !== 'true' && localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                    new Notification('Starbase Updates', {body: `Launch window for ${name} opens in 10 minutes!`});
                    localStorage.setItem('10minNotify-' + notifyKey, 'true');
                }
            }

            diff = openDiff;
        }

        const days = String(Math.floor(diff / (1000 * 60 * 60 * 24))).padStart(2, '0');
        const hours = String(Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
        const minutes = String(Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
        const seconds = String(Math.floor((diff % (1000 * 60)) / 1000)).padStart(2, '0');

        document.getElementById(id).innerHTML = `${name}:<br><span class="countdown">${days}:${hours}:${minutes}:${seconds}</span>`;

        const countdown = document.querySelector(`#${id} .countdown`);
        if (openDiff < 0) {
            countdown.style.color = "rgb(19, 159, 24)";
        } else {
            countdown.style.color = "";
        }
    }

    updateCountdown();
    activeTimers[id] = setInterval(updateCountdown, 1000);
}