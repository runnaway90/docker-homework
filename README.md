# docker-homework
Data engineering zoomcamp - week 1 homework


Question 1. Understanding Docker images
Run docker with the python:3.13 image. Use an entrypoint bash to interact with the container.

What's the version of pip in the image?

25.3
24.3.1
24.2.1
23.3.1
    ANSWER: 
    echo "PS1='> '" > ~/.bashrc
    PS1='> '
    docker run -it --entrypoint=bash python:3.13 
    root@cc7e7ee1ae06:/# python -V
    Python 3.13.13
    root@cc7e7ee1ae06:/# pip -V
    pip 26.0.1 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)



Question 2. Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?

services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
postgres:5433
localhost:5432
db:5433
postgres:5432
db:5432
If multiple answers are correct, select any


    Answer: db:5432

Prepare the Data
Download the green taxi trips data for November 2025:

wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
You will also need the dataset with zones:

wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv


    download files
    create docker-compose.yaml file and copy content
    docker-compose up
    both postgres and pgadmin and up. login on pgadmin with credentials.

    create load_data.py
    pip install pyarrow
    pip install uv
    uv init --python=3.13
    uv run which python
    ---> /workspaces/docker-homework/.venv/bin/python
    > which python        # System Python
    ---> /home/codespace/.python/current/bin/python
    uv add pandas pyarrow
    git status
    git add . 
    > git commit -m "setting up infrastructure"
    > git push

    add *.parquet and .csv to .gitignore file

    uv add --dev jupyter

    uv run jupyter notebook 

    Open 127.0.0.1:8888

    > uv add pandas

    load_data.py
        import pandas as pd
        df = pd.read_parquet('/workspaces/docker-homework/green_tripdata_2025-11.parquet')
        print(df.head())
    > uv run python3 load_data.py 
    > uv add sqlalchemy
        from sqlalchemy import create_engine
        engine = create_engine('postgresql+psycopg://postgres:postgres@localhost:5433/ny_taxi')
        print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
    > uv add psycopg
    import data to database.
        import pandas as pd
        df = pd.read_parquet('/workspaces/docker-homework/green_tripdata_2025-11.parquet')
        print(df.head())
        from sqlalchemy import create_engine
        engine = create_engine('postgresql+psycopg://postgres:postgres@localhost:5433/ny_taxi')
        print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))

        # Create table schema (no data)
        df.head(0).to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

        # Insert chunk
        df.to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="append"
        )

        print("Inserted:", len(df))

        df = pd.read_csv('/workspaces/docker-homework/taxi_zone_lookup.csv')

        # Create table schema (no data)
        df.head(0).to_sql(
            name="zones",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

        # Insert chunk
        df.to_sql(
            name="zones",
            con=engine,
            if_exists="append"
        )

        print("Inserted:", len(df)) 


Question 3. Counting short trips
For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?

7,853
8,007
8,254
8,421

    select count(*) from yellow_taxi_data ytd 
    where 
        ytd.lpep_pickup_datetime >= '2025-11-01' and
        ytd.lpep_pickup_datetime < '2025-12-01' and 
        ytd.trip_distance <= 1

    Answer 8007

Question 4. Longest trip for each day
Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

2025-11-14
2025-11-20
2025-11-23
2025-11-25
    select date(ytd.lpep_pickup_datetime) from yellow_taxi_data ytd 
    where trip_distance < 100
    order by trip_distance desc
    limit 1

    Answer: 2025-11-14
    
Question 5. Biggest pickup zone
Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

East Harlem North
East Harlem South
Morningside Heights
Forest Hills
¨
    select ans."Zone" 
    from (
        select puzones."Zone", sum(ytd.total_amount)
        from yellow_taxi_data ytd, zones puzones
        where ytd."PULocationID"  = puzones."LocationID" 
        group by puzones."Zone"
        order by 2 desc
        limit 1) as ans


    Answer: East Harlem North


Question 6. Largest tip
For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

Note: it's tip , not trip. We need the name of the zone, not the ID.

JFK Airport
Yorkville West
East Harlem North
LaGuardia Airport

    select dozones."Zone" from zones dozones, (select * 
    from yellow_taxi_data ytd, zones puzons
    where 
    puzons."Zone" = 'East Harlem North' and
    ytd."PULocationID" =puzons."LocationID" 
    order by tip_amount desc
    limit 1) as res
    where dozones."LocationID"  = res."DOLocationID"  

    Answer: Yorkville West



Terraform
In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. Copy the files from the course repo here to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.

Question 7. Terraform Workflow
Which of the following sequences, respectively, describes the workflow for:

Downloading the provider plugins and setting up backend,
Generating proposed changes and auto-executing the plan
Remove all resources managed by terraform`
Answers:

terraform import, terraform apply -y, terraform destroy
teraform init, terraform plan -auto-apply, terraform rm
terraform init, terraform run -auto-approve, terraform destroy, terraform init, terraform apply -auto-approve, terraform destroy
terraform import, terraform apply -y, terraform rm
