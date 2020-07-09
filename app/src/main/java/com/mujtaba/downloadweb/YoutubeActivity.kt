package com.mujtaba.downloadweb

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.webkit.WebView
import kotlinx.android.synthetic.main.activity_youtube.*

class YoutubeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_youtube)
        val youtubeView = WebView(this)
        setContentView(youtubeView)

        youtubeView.loadUrl("https://www.youtube.com/")

        youtubeView.settings.javaScriptEnabled= true


        dwBtn.setOnClickListener {
            val intentDw = Intent(this,MainActivity::class.java)
            startActivity(intentDw)
        }
    }
}