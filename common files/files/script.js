function doclist(id) {
	for (let li of document.querySelector("div.content").querySelectorAll("li.active")) { li.classList.remove("active"); }
	for (let d of document.getElementsByClassName("doclist")) {if (d.id != id + "docs") {d.style.display = "none";}}
	d = document.getElementById(id + "docs");
	if (d.style.display != "block" || d.style.display == "") {
		d.style.display = "block";
		document.getElementById(id).classList.add("active");
		
	} else {
		d.style.display = "none";
		document.getElementById(id).classList.remove("active");
	}
}