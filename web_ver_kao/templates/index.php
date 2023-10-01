


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index Page</title>

    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha1/css/bootstrap.min.css" integrity="sha384-r4NyP46KrjDleawBgD5tp8Y7UzmLA05oM1iAEQ17CSuDqnUK2+k9luXQOfXJCJ4I" crossorigin="anonymous">
</head>
<body>
    
<section>

    <div class="container">
    <h1 class="mt-5">Bed Infomation and Management Page</h1>
    <a href="insert_bed" class="btn btn-success">Go to Insert Bed</a> <a href="/admin" class="btn btn-secondary">Back to Admin Session</a>
    <hr>

    <div class="container">
        <form method="get">
            <!-- ช่องเลือกประเภทเตียง -->
            <select class="form-select form-select-sm" name="bed_type" aria-label="Select Bed Type">
                <option value="" selected>Select Bed Type</option>
                <option value="Standard">Standard</option>
                <option value="I.C.U">I.C.U</option>
                <option value="C.C.U">C.C.U</option>
            </select>

            <br>

            <!-- ช่องเลือกแผนก -->
            <select class="form-select form-select-sm" name="dept_name" aria-label="Select Department">
                <option value="" selected>Select Department</option>
                <option value="ศูนย์บรรจุผู้ป่วย">ศูนย์บรรจุผู้ป่วย</option>
                <option value="อายุรศาสตร์">อายุรศาสตร์</option>
                <option value="ศัลยศาสตร์">ศัลยศาสตร์</option>
                <option value="สูติศาสตร์-นรีเวชวิทยา">สูติศาสตร์-นรีเวชวิทยา</option>
                <option value="กุมารเวชกรรม">กุมารเวชกรรม</option>
                <option value="ศูนย์โรคหัวใจ">ศูนย์โรคหัวใจ</option>
                <option value="พิเศษ">พิเศษ</option>
            </select>

            <br>
            
            <!-- ช่องเลือกสถานะเตียง -->
            <select class="form-select form-select-sm" name="bed_status" aria-label="Select Bed Status">
                <option value="" selected>Select Bed Status</option>
                <option value="ว่าง">ว่าง</option>
                <option value="ไม่ว่าง">ไม่ว่าง</option>
            </select>

            <br>

            <button type="submit" class="btn btn-primary">Filter</button>
        </form>
    </div>




    <br>
    <hr>

    <!-- เพิ่มช่องค้นหา -->
    <div class="mb-3">
        <input type="text" id="searchInput" class="form-control" placeholder="Search...">
    </div>

    <form method="get">
        <label for="per_page">Show entries per page:</label>
        <select name="per_page" id="per_page">
            <option value="9999999" {% if selected_per_page == 0 %}selected{% endif %}>All</option>
            <option value="10" {% if selected_per_page == 10 %}selected{% endif %}>10</option>
            <option value="20" {% if selected_per_page == 20 %}selected{% endif %}>20</option>
            <option value="30" {% if selected_per_page == 30 %}selected{% endif %}>30</option>
    </select>
        <button type="submit" class="btn btn-primary">Apply</button>
    </form>

    <table id="mytable" class="table table-bordered table-striped">
        <thead>
            <th>Bed ID</th>
            <th>Room ID</th>
            <th>Bed Type</th>
            <th>Bed Status</th>
            <th>Department Name</th>

            <th>Edit</th>
            <th>Delete</th>
        </thead>
        <tbody>
            {% for bed in beds_data.items %}

            <tr>
                <td>{{ bed.bed_id }}</td>
                <td>{{ bed.room_id }}</td>
                <td>{{ bed.bed_type }}</td>
                <td>{{ bed.bed_status }}</td>
                <td>{{ bed.dept_name }}</td>
                <td><a href="{{ url_for('edit_bed', bed_id=bed.bed_id) }}" class="btn btn-primary">Edit</a></td>
                <td><a href="{{ url_for('delete_bed', bed_id=bed.bed_id) }}" class="btn btn-danger">Delete</a></td>
            </tr>

            {% endfor %}
        </tbody>
    </table>
    </div>


    <script>
        // ค้นหาเมื่อพิมพ์ในช่องค้นหา
        document.getElementById("searchInput").addEventListener("input", function () {
            let filter = this.value.toLowerCase();
            let rows = document.querySelectorAll("#mytable tbody tr");

            rows.forEach(row => {
                let text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = "table-row";
                } else {
                    row.style.display = "none";
                }
            });
        });
    </script>


    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha1/js/bootstrap.min.js" integrity="sha384-oesi62hOLfzrys4LxRF63OJCXdXDipiYWBnvTl9Y9/TRlw5xlKIEHpNyvvDShgf/" crossorigin="anonymous"></script>

</section>

</body>
</html>