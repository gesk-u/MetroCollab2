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


document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('skillForm');
    console.log(form)
    if (form) {
        const formContent = document.getElementById('student-form-content');
        const loadingScreen = document.getElementById('loadingScreen');
        const submitBtn = document.getElementById('student_form_btn');

        form.addEventListener('submit', function(e){
            e.preventDefault()
            console.log("3")

            submitBtn.disabled = true;

            formContent.classList.add('hidden');
            loadingScreen.classList.add('active');

            // Get form data
            const formData = new FormData(form);
            const userId = form.dataset.userId;
            console.log("4")
            console.log(userId)

            fetch(`/student_form/${userId}`, {
                method: 'POST',
                body: formData
            })

            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                return response.json();

            })

            .then(data => {
                setTimeout(() => {
                    //window.location.href = '/thank-you';
                    loadingScreen.innerHTML = `
                        <div style="text-align: center;">
                            <div style="font-size: 60px; margin-bottom: 20px;">✅</div>
                            <div style="font-size: 24px; font-weight: 600; color: #22c55e; margin-bottom: 10px;">
                                Success!
                            </div>
                            <p style="color: #64748b;">
                                In the real app, you'd be redirected to the thank-you page now.
                            </p>
                            <button onclick="showForm()" style="margin-top: 20px; width: auto; padding: 10px 30px;">
                                Try Again
                            </button>
                        </div>
                    `;
                }, 2000);
            })

            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while submitting the form. Please try again.');
            });
        });
    }
});