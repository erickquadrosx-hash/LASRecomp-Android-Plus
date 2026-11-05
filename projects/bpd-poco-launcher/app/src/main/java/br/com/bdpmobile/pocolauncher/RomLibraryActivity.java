package br.com.bdpmobile.pocolauncher;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Locale;

public class RomLibraryActivity extends Activity {
    private static final int PICK_ROM = 431;
    private static final int BG = Color.rgb(8, 18, 34);
    private static final int SURFACE = Color.rgb(17, 33, 53);
    private static final int GOLD = Color.rgb(247, 207, 99);
    private static final int FG = Color.rgb(236, 243, 254);
    private static final int MUTED = Color.rgb(178, 194, 210);
    private static final String[] ENGINE_NAMES = {"Eden", "Citron", "Yuzu", "Sudachi"};
    private static final String[] ENGINE_PACKAGES = {
        "dev.eden.eden_emulator", "org.citron.citron_emu",
        "org.yuzu.yuzu_emu", "org.sudachi.sudachi_emu"
    };
    private static final String[] ENGINE_ACTIVITIES = {
        "org.yuzu.yuzu_emu.activities.EmulationActivity",
        "org.citron.citron_emu.activities.EmulationActivity",
        "org.yuzu.yuzu_emu.activities.EmulationActivity",
        "org.sudachi.sudachi_emu.activities.EmulationActivity"
    };
    private SharedPreferences prefs;
    private LinearLayout gameList;
    private Spinner backend;
    private TextView summary;

    private int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }

    private GradientDrawable panel() {
        GradientDrawable d = new GradientDrawable();
        d.setColor(SURFACE);
        d.setCornerRadius(dp(15));
        d.setStroke(dp(1), Color.rgb(42, 66, 89));
        return d;
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(size);
        t.setTextColor(color);
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setPadding(0, dp(3), 0, dp(6));
        return t;
    }

    private void add(LinearLayout parent, View child, int bottom) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        p.bottomMargin = dp(bottom);
        parent.addView(child, p);
    }

    private Button button(LinearLayout parent, String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setAllCaps(false);
        b.setText(label);
        b.setTextColor(BG);
        b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(GOLD));
        b.setOnClickListener(listener);
        add(parent, b, 6);
        return b;
    }

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        prefs = getSharedPreferences("switch_roms", MODE_PRIVATE);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(BG);
        LinearLayout root = new LinearLayout(this);
        root.setPadding(dp(18), dp(21), dp(18), dp(30));
        root.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(root);
        setContentView(scroll);

        add(root, text("◇  Biblioteca Pokémon", 25, GOLD, true), 4);
        add(root, text("Arquivos Nintendo Switch · NSP e XCI", 14, MUTED, false), 12);
        button(root, "＋ Adicionar ROM NSP ou XCI", v -> chooseRom());
        add(root, text("Emulador instalado:", 15, FG, true), 3);
        backend = new Spinner(this);
        String[] options = {"Automático", "Eden", "Citron", "Yuzu", "Sudachi", "Escolher aplicativo"};
        ArrayAdapter<String> a = new ArrayAdapter<>(this,
            android.R.layout.simple_spinner_dropdown_item, options);
        backend.setAdapter(a);
        backend.setSelection(Math.max(0, Math.min(5, prefs.getInt("backend", 0))));
        backend.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> p, View v, int pos, long id) {
                prefs.edit().putInt("backend", pos).apply();
            }
            @Override public void onNothingSelected(AdapterView<?> p) {}
        });
        add(root, backend, 14);

        summary = text("Carregando biblioteca...", 13, MUTED, false);
        add(root, summary, 8);
        gameList = new LinearLayout(this);
        gameList.setOrientation(LinearLayout.VERTICAL);
        add(root, gameList, 12);
        add(root, text("É necessário ter um emulador compatível e configurado no aparelho. O launcher não executa ROMs sozinho e não inclui chaves nem firmware.", 12, MUTED, false), 0);
        renderLibrary();
    }

    private void chooseRom() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION |
            Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        try { startActivityForResult(i, PICK_ROM); }
        catch (ActivityNotFoundException e) {
            Toast.makeText(this, "Seletor de arquivos indisponível.", Toast.LENGTH_LONG).show();
        }
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request != PICK_ROM || result != RESULT_OK || data == null) return;
        Uri u = data.getData();
        if (u == null || !"content".equalsIgnoreCase(u.getScheme())) {
            Toast.makeText(this, "Selecione um documento do armazenamento Android.", Toast.LENGTH_LONG).show();
            return;
        }
        String name = documentName(u);
        String lower = name.toLowerCase(Locale.ROOT);
        if (!lower.endsWith(".nsp") && !lower.endsWith(".xci")) {
            new AlertDialog.Builder(this).setTitle("Formato não compatível")
                .setMessage("Esta biblioteca aceita apenas arquivos .NSP e .XCI.")
                .setPositiveButton("Entendi", null).show();
            return;
        }
        try {
            getContentResolver().takePersistableUriPermission(
                u, Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (SecurityException e) {
            Toast.makeText(this, "O armazenamento pode exigir nova seleção futuramente.", Toast.LENGTH_LONG).show();
        }
        JSONArray games = getGames();
        for (int n = 0; n < games.length(); n++) {
            if (u.toString().equals(games.optJSONObject(n).optString("uri"))) {
                Toast.makeText(this, "Esta ROM já está cadastrada.", Toast.LENGTH_SHORT).show();
                return;
            }
        }
        if (games.length() >= 60) {
            Toast.makeText(this, "Limite de 60 arquivos.", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            JSONObject item = new JSONObject();
            item.put("uri", u.toString());
            item.put("name", name);
            item.put("size", documentSize(u));
            games.put(item);
            saveGames(games);
            renderLibrary();
        } catch (Exception e) {
            Toast.makeText(this, "Não foi possível registrar a ROM.", Toast.LENGTH_LONG).show();
        }
    }

    private String documentName(Uri u) {
        try (Cursor c = getContentResolver().query(u, new String[] {OpenableColumns.DISPLAY_NAME},
                null, null, null)) {
            if (c != null && c.moveToFirst() && !c.isNull(0)) return c.getString(0);
        } catch (Exception ignored) {}
        return "desconhecido";
    }

    private long documentSize(Uri u) {
        try (Cursor c = getContentResolver().query(u, new String[] {OpenableColumns.SIZE},
                null, null, null)) {
            if (c != null && c.moveToFirst() && !c.isNull(0)) return c.getLong(0);
        } catch (Exception ignored) {}
        return -1;
    }

    private JSONArray getGames() {
        try { return new JSONArray(prefs.getString("library", "[]")); }
        catch (Exception ignored) { return new JSONArray(); }
    }

    private void saveGames(JSONArray games) {
        prefs.edit().putString("library", games.toString()).apply();
    }

    private String formatSize(long bytes) {
        if (bytes < 0) return "Tamanho desconhecido";
        if (bytes >= 1073741824L)
            return String.format(Locale.ROOT, "%.2f GiB", bytes / 1073741824.0);
        return String.format(Locale.ROOT, "%.1f MiB", bytes / 1048576.0);
    }

    private void renderLibrary() {
        if (gameList == null || summary == null) return;
        JSONArray games = getGames();
        gameList.removeAllViews();
        summary.setText(games.length() == 0 ?
            "Nenhum jogo selecionado ainda." : games.length() + " arquivo(s) na biblioteca local.");
        for (int i = 0; i < games.length(); i++) {
            JSONObject item = games.optJSONObject(i);
            if (item == null) continue;
            String name = item.optString("name", "ROM");
            String url = item.optString("uri", "");
            final int index = i;
            LinearLayout tile = new LinearLayout(this);
            tile.setOrientation(LinearLayout.VERTICAL);
            tile.setPadding(dp(13), dp(12), dp(13), dp(12));
            tile.setBackground(panel());
            add(gameList, tile, 10);
            add(tile, text(name, 15, FG, true), 0);
            String ext = name.toLowerCase(Locale.ROOT).endsWith(".xci") ? "XCI" : "NSP";
            add(tile, text(ext + "  •  " + formatSize(item.optLong("size", -1)), 12, MUTED, false), 6);
            button(tile, "▶  JOGAR ROM", v -> playRom(url, name));
            Button rm = button(tile, "Remover da biblioteca", v -> removeRom(index, name));
            rm.setTextColor(FG);
            rm.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(46, 65, 88)));
        }
    }

    private void removeRom(int index, String name) {
        new AlertDialog.Builder(this).setTitle("Remover da biblioteca?")
            .setMessage(name + "\nO arquivo original e o save não serão apagados.")
            .setPositiveButton("Remover", (d,w) -> {
                JSONArray old = getGames();
                JSONArray next = new JSONArray();
                for (int i = 0; i < old.length(); i++) {
                    if (i != index && old.opt(i) != null) next.put(old.opt(i));
                }
                saveGames(next);
                renderLibrary();
            })
            .setNegativeButton("Cancelar", null).show();
    }

    private boolean installed(String pkg) {
        try {
            getPackageManager().getPackageInfo(pkg, 0);
            return true;
        } catch (PackageManager.NameNotFoundException e) {
            return false;
        }
    }

    private void playRom(String rom, String name) {
        Uri u = Uri.parse(rom);
        if (!"content".equalsIgnoreCase(u.getScheme())) {
            Toast.makeText(this, "Referência inválida. Selecione a ROM novamente.", Toast.LENGTH_LONG).show();
            return;
        }
        int mode = backend.getSelectedItemPosition();
        if (mode == 5) { chooseApp(u); return; }
        int n = mode - 1;
        if (mode == 0) {
            n = -1;
            for (int i = 0; i < ENGINE_PACKAGES.length; i++) {
                if (installed(ENGINE_PACKAGES[i])) { n = i; break; }
            }
        }
        if (n < 0 || !installed(ENGINE_PACKAGES[n])) {
            new AlertDialog.Builder(this).setTitle("Emulador não encontrado")
                .setMessage("O launcher reconhece arquivos NSP/XCI, mas não pode executá-los sem um emulador Nintendo Switch compatível e configurado.")
                .setPositiveButton("Escolher outro aplicativo", (d,w) -> chooseApp(u))
                .setNegativeButton("Entendi", null).show();
            return;
        }
        try {
            Intent launch = new Intent(Intent.ACTION_VIEW);
            launch.setClassName(ENGINE_PACKAGES[n], ENGINE_ACTIVITIES[n]);
            launch.setData(u);
            launch.setClipData(ClipData.newRawUri(name, u));
            launch.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(launch);
        } catch (Exception e) {
            new AlertDialog.Builder(this).setTitle("O emulador não aceitou a ROM")
                .setMessage("A interface de abertura do emulador pode variar entre versões. Tente abrir a biblioteca dentro dele ou use o seletor de aplicativos.")
                .setPositiveButton("Escolher aplicativo", (d,w) -> chooseApp(u))
                .setNegativeButton("Cancelar", null).show();
        }
    }

    private void chooseApp(Uri u) {
        try {
            Intent launch = new Intent(Intent.ACTION_VIEW);
            launch.setDataAndType(u, "application/octet-stream");
            launch.setClipData(ClipData.newRawUri("ROM", u));
            launch.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(Intent.createChooser(launch, "Abrir ROM com"));
        } catch (Exception e) {
            Toast.makeText(this, "Não foi encontrado um aplicativo que aceite essa ROM.", Toast.LENGTH_LONG).show();
        }
    }
}
