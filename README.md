# Simple Scrapping Scripts

This repository contains a collection of simple scripts used for scraping manga data and downloading it onto a local computer. These scripts were originally developed as a personal manga scraper for downloading manga into a local computer.

## Scripts

* `downloader_service.py`: This script can be used as a service to automate the process of downloading manga chapters. It checks the download queues and downloads the 10 oldest manga chapter queues into the computer.

* `checkhome.py`: This script can be used as a service to periodically check if there are newly added manga in the database and sync off missing chapters into the local computer. If there are no newly added manga, it checks the readmng site for newly updated manga and syncs off missing chapters.

* `sqlsqlsqlsql.py`: This script can be used to manually check all/individual manga and sync up missing chapters.

* `redownloader.py`: This script can be used to manually check the manga folder for corrupted/empty downloaded images and attempts to redownload.

* `sort.py`: This script can be used to sort manga chapters in the database.

* `mmsort.py`: This script can be used to manually sort all/individual manga chapters in the webserver database.

## How to Use

1. Clone this repository to your local machine using `git clone https://github.com/yourusername/simple-scraper.git`
2. Install the necessary dependencies using `pip install -r requirements.txt`
3. Run the desired script using `python scriptname.py`

## Contributing

Contributions are always welcome! If you have any ideas, suggestions or found a bug, feel free to submit an issue or a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.