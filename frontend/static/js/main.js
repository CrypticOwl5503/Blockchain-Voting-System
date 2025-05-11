// Main JavaScript for the Blockchain Voting System

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    if (typeof $().tooltip === 'function') {
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    // Candidate selection highlighting
    const candidateRadios = document.querySelectorAll('.custom-control-input');
    candidateRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove highlight from all options
            document.querySelectorAll('.custom-control').forEach(control => {
                control.classList.remove('bg-light');
            });
            
            // Add highlight to selected option
            if (this.checked) {
                this.closest('.custom-control').classList.add('bg-light');
            }
        });
    });
});
