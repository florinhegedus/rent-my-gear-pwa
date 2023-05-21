var navItems = document.querySelectorAll(".item");
navItems.forEach(function(e, i) {
	e.addEventListener("click", function(e) {
		navItems.forEach(function(e2, i2) {
			e2.classList.remove("active");
		})
		this.classList.add("active");
	});
});