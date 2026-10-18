name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v5
      - name: Set up Java 17
        uses: actions/setup-java@v5
        with:
          distribution: 'temurin'
          java-version: '17'
      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install System Dependencies
        run: |
          sudo apt update
          sudo apt install -y zip unzip python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev libltdl-dev automake
      - name: Install Buildozer
        run: |
          pip install --upgrade pip
          pip install buildozer Cython==0.29.36
      - name: Build APK
        run: |
          buildozer android debug
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: SmartGuard-APK
          path: bin/*.apk
