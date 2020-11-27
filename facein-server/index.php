<?php 

	session_start();

	// redirect to the user page if the user has already login
	// or logout the user if there is a logout params in url
	if(isset($_SESSION["username"])){
		if(isset($_GET["logout"])){
			session_destroy();
		} else {
			header("Location: /user.php");
			exit();
		}
	}

	include("header.php");
	include("config.php");
?>

<div class="login">
	<p class="my-1 title">FaceIN 
		<i class="fas fa-lock-open"></i></p> 
	<p class="mt-1 sub-title">QR code downloader</p>
	<form class="login-form" action="" method="post">
		<div>
			<i class="fas fa-user"></i>
			<input class="ml-4" type="text" name="username" placeholder="Enter your username" required>
		</div>
		<div class="mt-4">
			<i class="fas fa-key"></i>
			<input class="ml-4" type="password" name="password" placeholder="Enter your password" required>
		</div>
	    <div class="mt-4">
	    	<i class="fas fa-paper-plane"></i>
	    	<input class="ml-4" type="submit" value="Submit">
	    </div>
	</form>
	<p class="copy-right"><i class="fas fa-copyright"></i> Team Java Rice - All Rights Reserved 2019</p>

</div>

<?php 
	include ("footer.php");

	// detect login 
	if(isset($_POST["username"]) && isset($_POST["password"])){
			//compare username and password in the database
		    $statement = $connection->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
		    $pass = md5($_POST['password']);
		    $statement->bind_param('ss', $_POST['username'], $pass);
		    $statement->execute();
		    $result = $statement->get_result();
			$row = $result->fetch_assoc();
			if(isset($row)){
				$_SESSION['username'] = $row["username"];
				header("Location: /user.php");
			}
		}
?>