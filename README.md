# YoutubeDl-cut-no-links
YoutubeDl-get cut (or not) videos with no links(or links stv mais bon azi) using yt-dlp and requests
 
<strong>No-links</strong>
    Do a youtube search of the input and will show you the most relavants
videos linked to the search (user choose to download or go to the next one in the search)
    Can also enter a direct link to video/playlist

<strong>Cut</strong>
    Get a part of video (can be long if big part):
    cut(h:m:s / h:m:s) <'video'>
        start   end (/ not needed)

<strong>Format</strong>
    
    audio : mp3 (can be long to convert if big video so remove 'prefferedcodec' in options and change mp3 to webm in script if long)
    mp4 : wbem (long to mp4)

<strong>options</strong> (deja toutes par defaut fo regarder):

- audio/video: options, converted from webm to basic mp3 and leaves webm for
                 video files because otherwise too long
                (editable : change 'bv:ba to 'bestvideo+bestaudio/best' in options to getmp4)
- querySep: the separator to download several in a row
             (can make several requests in a row regardless of the type, format, number or if cut)
- playlistKW: the keyword in the input to specify that we are looking for a playlist

- videoKW: the keyword in the input to specify that we are looking for a video (wbem not mp3)

- changeKW: to change the request along the way (if it doesn't work because it's not precise enough)

- audio/videoSaveDirs: folders for audio/video (maybe the same)

- forceNames: have names without spaces(spaces become '_') and #

install requirements.txt
