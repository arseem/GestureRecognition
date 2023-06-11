function toggleGesture(gesture_id) {
    var label = document.querySelector(`label[for=gesture${gesture_id}]`);
    if (label.classList.contains("gesture-on")) {
        label.classList.remove("gesture-on");
        label.classList.add("gesture-off");
    } else {
        label.classList.remove("gesture-off");
        label.classList.add("gesture-on");
    }
}

function deleteGesture(gesture_id) {
    // Function to delete a gesture, yet to be implemented
    console.log("Deleting gesture with ID: " + gesture_id);
}

function toggleRecognition() {
    alert("Not implemented yet!");
}

function hideGui() {
    alert("Not implemented yet!");
}

function adjustGesturesListHeight() {
    var cameraFeedHeight = document.querySelector(".camera-feed").offsetHeight;
    var gesturesList = document.getElementById("gesturesList");
    gesturesList.style.maxHeight = cameraFeedHeight + "px";
}
function adjustCameraFeedSize() {
    var cameraFeed = document.querySelector(".camera-feed");
    var cameraFeedWidth = cameraFeed.offsetWidth;
    var cameraFeedHeight = cameraFeed.offsetHeight;
  
    var videoFrame = document.getElementById("videoFrame");
    videoFrame.src = "/video_feed?width=" + cameraFeedWidth + "&height=" + cameraFeedHeight;
  }

window.addEventListener('DOMContentLoaded', function() {
    adjustGesturesListHeight();
    adjustCameraFeedSize();
});
  
window.addEventListener('resize', function() {
    adjustGesturesListHeight();
    adjustCameraFeedSize();
});

 
function showPopup() {
    document.getElementById("popupContainer").style.display = "block";
}

function hidePopup() {
    document.getElementById("popupContainer").style.display = "none";
}

function saveGesture() {
    var gestureNameInput = document.getElementById("gestureName");
    var gestureName = gestureNameInput.value.trim();
    var gestureType = document.querySelector('input[name="gestureType"]:checked').value;
    var gesturesList = document.getElementById("gesturesList");

    if (gestureName === "") {
        gestureNameInput.classList.add("error");
        gestureNameInput.placeholder = "Please enter a valid gesture name";
        return;
    }

    for (var i = 0; i < gesturesList.children.length; i++) {
        var listItem = gesturesList.children[i];
        var listItemText = listItem.querySelector(".custom-control-label").textContent.trim();
        if (listItemText === gestureName) {
            gestureNameInput.classList.add("error");
            gestureNameInput.value = "";
            gestureNameInput.placeholder = "Gesture name already exists";
            return;
        }
    }

    // Perform any necessary actions with the captured gesture name and type
    window.location.href = "/record_gesture/" + gestureName + '/' + gestureType;
    hidePopup();
}

function cancelGesture() {
    // Close the popup window without saving
    hidePopup();
}

function recordGesture() {
    var gestureNameInput = document.getElementById("gestureName");
    gestureNameInput.classList.remove("error");
    gestureNameInput.value = "";
    gestureNameInput.placeholder = "Gesture Name";

    showPopup();
}