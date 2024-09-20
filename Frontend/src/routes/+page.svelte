<script>
    import { onMount } from 'svelte';
    let volume = 0;  // Volume variable
    let imgSrc = ''; // To hold the video frame
 
    // WebSocket logic to receive video frames and volume
    onMount(() => {
       const socket = new WebSocket('ws://localhost:8765');
       
       socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          volume = data.volume;
          imgSrc = data.frame; // This will be an image URL from the backend
       };
 
       socket.onerror = (error) => {
          console.log('WebSocket Error: ', error);
       };
 
       socket.onclose = () => {
          console.log('WebSocket connection closed');
       };
    });
 </script>
 
 <style>
    .volume-bar {
       width: 200px;
       height: 20px;
       background-color: lightgray;
       margin-top: 20px;
       position: relative;
    }
 
    .volume-fill {
       height: 100%;
       background-color: green;
    }
 
    .video-feed {
       width: 640px;
       height: 480px;
       margin-top: 20px;
    }
 
    img {
       width: 100%;
       height: auto;
    }
 </style>
 
 <div>
    <h1>Handtracking Volume Control</h1>
 
    <!-- Volume Bar -->
    <div class="volume-bar">
       <div class="volume-fill" style="width: {volume}%"></div>
    </div>
    <p>Volume: {volume}%</p>
 
    <!-- Video Feed -->
    <div class="video-feed">
       {#if imgSrc}
          <img src={imgSrc} alt="Video Feed" />
       {:else}
          <p>No video feed yet...</p>
       {/if}
    </div>
 </div>
 