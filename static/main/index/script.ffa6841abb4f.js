// document.querySelector('.header_moon').onclick = function() {
//     document.querySelector('body').classList.toggle('night');
// }

if (localStorage.getItem('theme') == 'dark') {
    setDarkMode();

    if (document.getElementById('moon').checked) {
        localStorage.setItem('moon', true)
    }
}

function setDarkMode() {
    let isDark = document.body.classList.toggle('night');

    if (isDark) {
        setDarkMode.checked = true;
        localStorage.setItem('theme' , 'night');
        document.getElementById('moon').setAttribute('checked', 'checked');
    } else {
        setDarkMode.checked = true;
        localStorage.removeItem('theme', 'night');
    }
}

 if (localStorage.getItem('theme') == 'dark') {
            setDarkMode();

            if (document.getElementById('moon').checked) {
                localStorage.setItem('moon', true)
            }
        }

        function setDarkMode() {
            let isDark = document.body.classList.toggle('night');

            if (isDark) {
                setDarkMode.checked = true;
                localStorage.setItem('theme' , 'night');
                document.getElementById('moon').setAttribute('checked', 'checked');
            } else {
                setDarkMode.checked = true;
                localStorage.removeItem('theme', 'night');
            }
        }