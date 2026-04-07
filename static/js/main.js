// Manejo de visibilidad de contraseñas (Ojito)
document.addEventListener('DOMContentLoaded', function() {
    const spyButtons = document.querySelectorAll('.input-group-text-spy');
    
    spyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye-fill', 'bi-eye-slash-fill');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash-fill', 'bi-eye-fill');
            }
        });
    });
});