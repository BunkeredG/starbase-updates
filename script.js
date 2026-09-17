// Temporary calls
startCountdown(format("09/22/12/15"), format("09/22/13/30"), 'hc', 'pc', 'Flight 14');
startCountdown(format("09/20/01/47"), format("09/20/06/30"), 'hc-s1527', 'pc-s1527', '(F9) Starlink 15-27');
startCountdown(format("09/26/11/56"), format("09/26/15/39"), 'hc-ussf385', 'pc-ussf385', '(F9) USSF-385');
const carouselIDS = ['r1', 'r2', 'r3'];
const carouselTimer = setInterval(() => carousel(carouselIDS), 5000);

// Dedicated Starship flight countdown
if (document.getElementById('starship')) {
    startCountdown(format("09/22/12/15"), format("09/22/13/30"), 'starship');
}

// Date converter (MM/DD/HH/mm in UTC)
function format(date) {
    // [0] -> month | [1] -> day | [2] -> hour | [3] -> minute
    const dateL = date.split('/');
    return `2026-${dateL[0]}-${dateL[1]}T${dateL[2]}:${dateL[3]}:00Z`;
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
function startCountdown(openDate, closeDate, id, preid=null, prem=null) {
    const windowOpen = new Date(openDate);
    const windowClose = new Date(closeDate);
    const notifyKey = windowOpen.toISOString();
    let timer;

    function updateCountdown() {
        const now = new Date();
        const openDiff = windowOpen - now;
        const closeDiff = windowClose - now;
        let diff;

        if (localStorage.getItem('closeNotify-' + notifyKey) === 'true') {
            if (prem) {
                document.getElementById(preid).textContent = `${prem}`;
            }
            document.getElementById(id).textContent = "(Window Closed)";
            document.getElementById(id).style.color = 'rgb(228, 17, 17)'
            clearInterval(timer);
            return;
        }

        if (closeDiff < 0) {
            if (prem && localStorage.getItem('closeNotify-' + notifyKey) !== 'true' && localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                new Notification('Starbase Updates', {body: `Launch window for ${prem} is closed`});
                localStorage.setItem('closeNotify-' + notifyKey, 'true');
            }
        }

        if (openDiff < 0) {
            if (prem && localStorage.getItem('openNotify-' + notifyKey) !== 'true' && localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                new Notification('Starbase Updates', {body: `Launch window for ${prem} is open!`});
                localStorage.setItem('openNotify-' + notifyKey, 'true');
            }

            diff = closeDiff;
            document.getElementById(id).style.color = 'rgb(19, 159, 24)';
        }

        if (openDiff - (1000 * 60 * 10) < 0) {
            if (prem && localStorage.getItem('10minNotify-' + notifyKey) !== 'true' && localStorage.getItem('subscribed') === 'true' && Notification.permission === 'granted') {
                new Notification('Starbase Updates', {body: `Launch window for ${prem} opens in 10 minutes!`});
                localStorage.setItem('10minNotify-' + notifyKey, 'true');
            }
        }

        if (openDiff > 0) {
            diff = openDiff;
            document.getElementById(id).style.color = '';
        }

        const days = String(Math.floor(diff / (1000 * 60 * 60 * 24))).padStart(2, '0');
        const hours = String(Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
        const minutes = String(Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
        const seconds = String(Math.floor((diff % (1000 * 60)) / 1000)).padStart(2, '0');

        if (prem) {
            document.getElementById(preid).textContent = `${prem}`;
            document.getElementById(id).textContent = `${days}:${hours}:${minutes}:${seconds}`;
        } else {
            document.getElementById(id).textContent = `(${days}:${hours}:${minutes}:${seconds})`;
        }
    }

    updateCountdown();
    timer = setInterval(updateCountdown, 1000);
}

// Launch carousel
let carouselIndex = 0;
function carousel(ids) {
    const currentID = ids[carouselIndex];
    carouselIndex = (carouselIndex + 1) % ids.length;
    const nextID = ids[carouselIndex];

    document.getElementById(currentID).classList.remove('visible');
    document.getElementById(nextID).classList.add('visible');
}