FROM archlinux/archlinux:base-devel

RUN pacman -Syu --needed --noconfirm git

# makepkg user and workdir
ARG user=makepkg
RUN useradd --system --create-home $user \
  && echo "$user ALL=(ALL:ALL) NOPASSWD:ALL" > /etc/sudoers.d/$user
USER $user
WORKDIR /home/$user



# Install yay
RUN git clone https://aur.archlinux.org/yay.git \
  && cd yay \
  && makepkg -sri --needed --noconfirm \
  && cd \
  # Clean up
  && rm -rf .cache yay

RUN yay -Syu --needed --noconfirm gr-lora_sdr python-pip

COPY requirements.txt ./
COPY apps/runner.py .
COPY apps/cran_recieve.py .

#Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# run the command
CMD [ "python", "./runner.py"]

# tell the port number the container should expose
EXPOSE 5555/tcp