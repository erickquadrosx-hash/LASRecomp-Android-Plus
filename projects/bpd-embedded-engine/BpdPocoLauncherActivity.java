// SPDX-License-Identifier: GPL-3.0-or-later
// Launcher adicional para o núcleo GPL Lemon, sem dados de jogos.
package dev.lemon.lemon_emu.activities;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Locale;
import org.json.JSONArray;
import org.json.JSONObject;

public final class BpdPocoLauncherActivity extends Activity {
    private static final int PICK_ROM = 801;
    private static final int BG = Color.rgb(9,19,33), PANEL = Color.rgb(24,41,60);
    private static final int FG = Color.rgb(240,246,254), GOLD = Color.rgb(245,201,95);
    private SharedPreferences prefs;
    private LinearLayout romList;
    private TextView count;

    private int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }
    private TextView text(String s, int size, int color, boolean strong) {
        TextView v = new TextView(this);
        v.setText(s); v.setTextSize(size); v.setTextColor(color);
        v.setPadding(0,dp(4),0,dp(8));
        if(strong) v.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        return v;
    }
    private void add(LinearLayout l, View v, int margin) {
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);
        p.bottomMargin=dp(margin); l.addView(v,p);
    }
    private Button action(LinearLayout l, String label, boolean primary, View.OnClickListener cb) {
        Button v=new Button(this); v.setAllCaps(false); v.setText(label); v.setTextSize(15);
        v.setTextColor(primary?BG:FG);
        v.setBackgroundTintList(ColorStateList.valueOf(primary?GOLD:Color.rgb(50,72,97)));
        v.setOnClickListener(cb); add(l,v,6); return v;
    }
    private LinearLayout panel(LinearLayout root,String title) {
        LinearLayout p=new LinearLayout(this); p.setOrientation(LinearLayout.VERTICAL);
        p.setPadding(dp(16),dp(12),dp(16),dp(14));
        GradientDrawable d=new GradientDrawable(); d.setColor(PANEL);
        d.setCornerRadius(dp(16)); p.setBackground(d);
        add(root,p,13); add(p,text(title,16,GOLD,true),5); return p;
    }
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        prefs=getSharedPreferences("bpd_poco_games",MODE_PRIVATE);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        ScrollView scroll=new ScrollView(this); scroll.setBackgroundColor(BG);
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18),dp(22),dp(18),dp(30));
        scroll.addView(root); setContentView(scroll);
        add(root,text("◆ BPD POCO CORE",25,GOLD,true),2);
        add(root,text("Motor Lemon Lite integrado • ARM64 • Vulkan",13,FG,false),15);
        LinearLayout play=panel(root,"Jogar ROMs Pokémon");
        action(play,"＋ Selecionar NSP ou XCI",true,v->pickRom());
        action(play,"Abrir menu completo do emulador",false,v->emulatorHome());
        add(play,text("Os jogos de Switch são emulados pelo núcleo integrado. Não é um port nativo dos jogos.",12,FG,false),0);
        LinearLayout library=panel(root,"Minha biblioteca");
        count=text("",13,FG,false); add(library,count,5);
        romList=new LinearLayout(this);romList.setOrientation(LinearLayout.VERTICAL);
        add(library,romList,6);
        refresh();
        LinearLayout about=panel(root,"Desempenho e informações");
        add(about,text("Perfil: POCO X7 Pro / Dimensity 8400-Ultra / Mali-G720. Comece com 30 FPS e escala 1× ou inferior nas configurações gráficas do Lemon.",13,FG,false),5);
        add(about,text("Emulador open-source Lemon (GPL-3.0-or-later). ROMs, firmware e chaves não estão incluídos. Use somente arquivos legitimamente obtidos.",12,FG,false),0);
    }
    private JSONArray library() {
        try {return new JSONArray(prefs.getString("roms","[]"));}
        catch(Exception e){return new JSONArray();}
    }
    private void save(JSONArray a){prefs.edit().putString("roms",a.toString()).apply();}
    private void pickRom() {
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("*/*");
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        try{startActivityForResult(i,PICK_ROM);}
        catch(Exception e){Toast.makeText(this,"Não foi possível abrir o seletor.",Toast.LENGTH_LONG).show();}
    }
    private String name(Uri uri) {
        try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)) {
            if(c!=null&&c.moveToFirst()) return c.getString(0);
        }catch(Exception ignored){}
        return "ROM sem nome";
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request!=PICK_ROM||result!=RESULT_OK||data==null)return;
        Uri uri=data.getData();
        if(uri==null||!"content".equals(uri.getScheme()))return;
        String name=name(uri),lower=name.toLowerCase(Locale.ROOT);
        if(!lower.endsWith(".nsp")&&!lower.endsWith(".xci")) {
            Toast.makeText(this,"Escolha um arquivo NSP ou XCI.",Toast.LENGTH_LONG).show();return;
        }
        try{getContentResolver().takePersistableUriPermission(uri,Intent.FLAG_GRANT_READ_URI_PERMISSION);}
        catch(SecurityException ignored){}
        JSONArray list=library();
        for(int i=0;i<list.length();i++) {
            JSONObject item=list.optJSONObject(i);
            if(item!=null&&uri.toString().equals(item.optString("uri")))return;
        }
        if(list.length()>=60){Toast.makeText(this,"Biblioteca cheia.",Toast.LENGTH_LONG).show();return;}
        try{
            JSONObject item=new JSONObject();item.put("uri",uri.toString());item.put("name",name);
            list.put(item);save(list);refresh();
        }catch(Exception e){Toast.makeText(this,"Erro ao cadastrar jogo.",Toast.LENGTH_LONG).show();}
    }
    private void refresh(){
        if(romList==null)return;
        romList.removeAllViews();JSONArray arr=library();
        count.setText(arr.length()==0?"Nenhum jogo cadastrado.":arr.length()+" jogo(s) selecionados.");
        for(int i=0;i<arr.length();i++){
            JSONObject item=arr.optJSONObject(i);if(item==null)continue;
            String title=item.optString("name","ROM"),link=item.optString("uri","");
            final int index=i;
            LinearLayout tile=new LinearLayout(this);tile.setOrientation(LinearLayout.VERTICAL);
            add(romList,tile,10);add(tile,text(title,14,FG,true),2);
            action(tile,"▶ JOGAR",true,v->play(link));
            action(tile,"Remover da lista",false,v->remove(index));
        }
    }
    private void remove(int index) {
        JSONArray old=library(),fresh=new JSONArray();
        for(int i=0;i<old.length();i++)if(i!=index&&old.opt(i)!=null)fresh.put(old.opt(i));
        save(fresh);refresh();
    }
    private void play(String file){
        Uri uri=Uri.parse(file);
        if(!"content".equals(uri.getScheme()))return;
        Intent launch=new Intent(Intent.ACTION_VIEW,uri);
        launch.setClassName(getPackageName(),"dev.lemon.lemon_emu.activities.EmulationActivity");
        launch.setClipData(ClipData.newRawUri("Switch ROM",uri));
        launch.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try{startActivity(launch);}
        catch(Exception e){
            new AlertDialog.Builder(this).setTitle("Não foi possível iniciar o jogo")
                .setMessage("Abra o menu completo do Lemon para configurar o motor e verificar os dados do jogo.")
                .setPositiveButton("OK",null).show();
        }
    }
    private void emulatorHome() {
        Intent i=new Intent();
        i.setClassName(getPackageName(),"dev.lemon.lemon_emu.ui.main.MainActivity");
        try{startActivity(i);}
        catch(Exception e){Toast.makeText(this,"Menu do emulador indisponível.",Toast.LENGTH_LONG).show();}
    }
}
