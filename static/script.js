let selectedRole = null;

function selectRole(element, role) {
    // Remove previous selection
    document.querySelectorAll('.role-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selection to clicked element
    element.classList.add('selected');
    selectedRole = role;
    
    // Update hidden form field
    document.getElementById('selectedRole').value = role;
    
    // Show continue button
    const continueBtn = document.getElementById('continueBtn');
    continueBtn.classList.add('visible');
}


function handleSubmit(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const userlastname = document.getElementById('userlastname').value;

    // Validate
    if (!username || !userlastname) {
        alert('Please enter your name and last name');
        return;
    }

    if (!selectedRole) {
        alert('Please select your role!');
        return;
    }

    const formData = new FormData();
    formData.append('username', username);
    formData.append('lastname', userlastname);
    formData.append('selectedRole', selectedRole);

    fetch('/', {
        method: 'POST',
        body: formData 
    })
    .then(response => response.text())
    .then(data => {
        // Hide selection screen with fade out
        const selectionScreen = document.getElementById('selectionScreen');
        selectionScreen.style.opacity = '0';
        selectionScreen.style.transform = 'translateY(-20px)';

        setTimeout(() => {
            selectionScreen.style.display = 'none';

            // Show appropriate dashboard with fade in
            const fullName = `${username} ${userlastname}`;

            if (selectedRole === 'student') {
                const studentDashboard = document.getElementById('studentDashboard');
                document.getElementById('studentName').textContent = fullName;
                studentDashboard.style.display = 'flex';
                setTimeout(() => {
                    studentDashboard.style.opacity = '1';
                    studentDashboard.style.transform = 'translateY(0)';
                }, 10);
            } else {
                const teacherDashboard = document.getElementById('teacherDashboard');
                document.getElementById('teacherName').textContent = fullName;
                teacherDashboard.style.display = 'flex';
                setTimeout(() => {
                    teacherDashboard.style.opacity ='1';
                    teacherDashboard.style.transform = 'translateY(0)';
                }, 10);
            }
        }, 300);
    })

    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}


// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && selectedRole) {
        const username = document.getElementById('username').value;
        const userlastname = document.getElementById('userlastname').value;
        if (username && userlastname) {
            handleSubmit(e);
        }
    }
});


const otherCheckbox = document.getElementById('otherCheckbox');
const otherText = document.getElementById('otherText');
const form = document.getElementById('skillForm');

otherCheckbox.addEventListener("change", () => {
    if (otherCheckbox.checked) {
        otherText.disabled = false;
        otherText.focus();
    }
    else {
        otherText.disabled = true;
        otherText.value = "";
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      // You can add more conditions here if needed, e.g. check if username and lastname are filled
      e.preventDefault(); // prevent default Enter key behavior like form submit or newlines
      form.submit();
    }
});