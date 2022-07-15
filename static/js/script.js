window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteButton = document.querySelectorAll(".btnDelete");
for (let x = 0; x < deleteButton.length; x++) {
  const btn = deleteButton[x];
  btn.onclick = function (e) {
    const venue_id = e.target.dataset["id"];
    console.log(venue_id);
    fetch("/venues/" + venue_id, {
      method: "DELETE",
    })
      .then((response) => (window.location.href = "/"))
      .catch((err) => console.log("error deleting the venue"));
  };
}
