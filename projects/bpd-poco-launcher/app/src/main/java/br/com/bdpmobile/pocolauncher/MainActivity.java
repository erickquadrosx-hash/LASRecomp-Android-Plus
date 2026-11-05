package br.com.bdpmobile.pocolauncher;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.content.res.ColorStateList;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final int PICK_ZIP = 42;
    private static final int BACK = Color.rgb(8, 18, 34);
    private static final int SURFACE = Color.rgb(17, 33, 53);
    private static final int GOLD = Color.rgb(247, 207, 99);
    private static final int TEXT = Color.rgb(236, 243, 254);
    private static final int MUTED = Color.rgb(178, 194, 210);
    private EditText packageInput;
    private TextView statusText;
    private TextView dataText;
    private TextView profileText;
    private Spinner profilePicker;
    private SharedPreferences prefs;

    private int dp(int n) {
        return Math.round(n * getResources().getDisplayMetrics().density);
    }

    private GradientDrawable shape(int color, int border) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color);
        d.setCornerRadius(dp(18));
        if (border != 0) d.setStroke(dp(1), border);
        return d;
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(size);
        t.setTextColor(color);
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        t.setPadding(0, dp(4), 0, dp(7));
        return t;
    }

    private void add(LinearLayout layout, View child, int margin) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        p.bottomMargin = dp(margin);
        layout.addView(child, p);
    }

    private LinearLayout card(LinearLayout root, String heading) {
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16), dp(15), dp(16), dp(15));
        panel.setBackground(shape(SURFACE, Color.rgb(43, 60, 82)));
        add(root, panel, 14);
        add(panel, text(heading, 17, GOLD, true), 9);
        return panel;
    }

    private Button button(LinearLayout parent, String title, boolean primary, View.OnClickListener action) {
        Button b = new Button(this);
        b.setText(title);
        b.setAllCaps(false);
        b.setTextSize(15);
        b.setTextColor(primary ? BACK : TEXT);
        b.setBackgroundTintList(ColorStateList.valueOf(primary ? GOLD : Color.rgb(39, 60, 84)));
        b.setOnClickListener(action);
        add(parent, b, 6);
        return b;
    }

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences("launcher", MODE_PRIVATE);
        getWindow().setStatusBarColor(BACK);
        getWindow().setNavigationBarColor(BACK);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(BACK);
        LinearLayout root = new LinearLayout(this);
        root.setPadding(dp(18), dp(23), dp(18), dp(30));
        root.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(root);
        setContentView(scroll);

        add(root, text("◇  BPD POCO LAUNCHER", 25, GOLD, true), 1);
        add(root, text("Pokémon Brilliant Diamond Mobile · POCO X7 Pro", 14, MUTED, false), 14);

        LinearLayout play = card(root, "Jogar");
        statusText = text("Verificando aplicativo...", 14, MUTED, false);
        add(play, statusText, 6);
        button(play, "▶  JOGAR AGORA", true, v -> launchGame());
        button(play, "Localizar BPD Mobile instalado", false, v -> findGame());
        add(play, text("O jogo roda no aplicativo BPD Mobile instalado separadamente. Este launcher não executa ROMs sozinho.", 12, MUTED, false), 0);

        LinearLayout roms = card(root, "Jogos Pokémon · NSP / XCI");
        add(roms, text("Biblioteca local de arquivos NSP e XCI, com abertura via emulador Android instalado.", 13, MUTED, false), 5);
        button(roms, "🎮  ABRIR BIBLIOTECA DE ROMS", true,
            v -> startActivity(new Intent(this, RomLibraryActivity.class)));
        add(roms, text("O launcher não contém emulador, ROMs nem chaves. Instale separadamente um emulador compatível.", 12, MUTED, false), 0);

        LinearLayout setup = card(root, "Preparar os dados do jogo");
        dataText = text("Nenhum ZIP selecionado.", 13, MUTED, false);
        add(setup, dataText, 5);
        button(setup, "Selecionar BDP_MOBILE_DATA.zip", false, v -> pickZip());
        button(setup, "Abrir BPD Mobile para importar os dados", false, v -> {
            new AlertDialog.Builder(this)
                .setTitle("Importação no jogo original")
                .setMessage("Na tela do BPD Mobile, use o seletor de arquivos interno e escolha BDP_MOBILE_DATA.zip. O launcher apenas lembra a localização do arquivo; ele não o importa nem o extrai.")
                .setPositiveButton("Abrir BPD Mobile", (d, which) -> launchGame())
                .setNegativeButton("Cancelar", null).show();
        });
        add(setup, text("O ZIP pode ter vários GB. Nada será enviado ao GitHub ou copiado pelo launcher.", 12, MUTED, false), 0);

        LinearLayout tuning = card(root, "Perfil de desempenho");
        add(tuning, text("Configuração inicial sugerida: resolução interna de 1280 px e 30 FPS pelo menu do próprio jogo.", 13, MUTED, false), 8);
        profilePicker = new Spinner(this);
        String[] choices = {"Equilibrado · 90% / 30 FPS", "Desempenho · 80% / 30 FPS", "Padrão do jogo / restaurar"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
            android.R.layout.simple_spinner_dropdown_item, choices);
        profilePicker.setAdapter(adapter);
        profilePicker.setSelection(Math.max(0, Math.min(2, prefs.getInt("profile", 0))));
        add(tuning, profilePicker, 5);
        profileText = text("", 13, MUTED, false);
        add(tuning, profileText, 8);
        profilePicker.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                prefs.edit().putInt("profile", position).apply();
                updateProfile();
            }
            @Override public void onNothingSelected(AdapterView<?> parent) {}
        });
        updateProfile();
        button(tuning, "Copiar comando ADB do perfil", false, v -> copyCommand(false));
        button(tuning, "Copiar comando para restaurar", false, v -> copyCommand(true));
        add(tuning, text("Comandos ADB são opcionais, exigem computador ou depuração autorizada e podem não surtir efeito no HyperOS. Nenhum ajuste é aplicado automaticamente.", 12, MUTED, false), 0);

        LinearLayout other = card(root, "Diagnóstico e configuração");
        packageInput = new EditText(this);
        packageInput.setSingleLine(true);
        packageInput.setTextColor(TEXT);
        packageInput.setHintTextColor(MUTED);
        packageInput.setHint("Pacote Android do jogo");
        packageInput.setText(prefs.getString("package", ""));
        add(other, packageInput, 7);
        add(other, text("Se o aplicativo não for encontrado automaticamente, insira o nome do pacote instalado.", 12, MUTED, false), 8);
        button(other, "Salvar identificação do jogo", false, v -> {
            savePackage();
            updateStatus();
        });
        button(other, "Copiar diagnóstico do aparelho", false, v -> copy(deviceInfo()));
        add(other, text(deviceInfo(), 12, MUTED, false), 0);

        add(root, text("Versão 0.3 · Biblioteca NSP/XCI e BPD Mobile · Sem ROMs embutidas", 12, MUTED, false), 0);
        updateData();
        updateStatus();
    }

    private void updateProfile() {
        if (profileText == null || profilePicker == null) return;
        int p = profilePicker.getSelectedItemPosition();
        if (p == 1) profileText.setText("Mais leve: downscale externo 80%. Priorize estabilidade gráfica.");
        else if (p == 2) profileText.setText("Mantém as configurações de renderização controladas pelo jogo.");
        else profileText.setText("Equilibrado: downscale externo 90%. Meta de 30 FPS.");
    }

    private String packageName() {
        return packageInput == null ? prefs.getString("package", "") :
            packageInput.getText().toString().trim();
    }

    private void savePackage() {
        prefs.edit().putString("package", packageName()).apply();
    }

    private void updateStatus() {
        if (statusText == null) return;
        String pkg = packageName();
        if (pkg.isEmpty()) {
            statusText.setText("Escolha o aplicativo BPD Mobile instalado.");
            return;
        }
        Intent launch = getPackageManager().getLaunchIntentForPackage(pkg);
        statusText.setText(launch != null ? "Pronto para jogar · " + pkg :
            "Aplicativo não encontrado: " + pkg);
    }

    private void findGame() {
        PackageManager pm = getPackageManager();
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> list = pm.queryIntentActivities(intent, 0);
        ArrayList<String> packages = new ArrayList<>();
        ArrayList<String> names = new ArrayList<>();
        for (ResolveInfo r : list) {
            if (r.activityInfo == null) continue;
            String pkg = r.activityInfo.packageName;
            CharSequence labelObj = r.loadLabel(pm);
            String label = labelObj == null ? "" : labelObj.toString();
            String match = (pkg + " " + label).toLowerCase(Locale.ROOT);
            if (match.contains("bpd") || match.contains("bdsp") ||
                match.contains("brilliant") || match.contains("diamond") ||
                match.contains("pokemon") || match.contains("pokémon")) {
                if (!packages.contains(pkg) && !pkg.equals(getPackageName())) {
                    packages.add(pkg);
                    names.add(label + "\n" + pkg);
                }
            }
        }
        if (packages.isEmpty()) {
            new AlertDialog.Builder(this)
                .setTitle("Port não detectado")
                .setMessage("Instale primeiro seu bpdpkg1.1.apk e informe o nome do pacote Android do jogo no campo inferior. Não é necessário enviar o ZIP de dados.")
                .setPositiveButton("Entendi", null).show();
            return;
        }
        new AlertDialog.Builder(this)
            .setTitle("Escolha o jogo instalado")
            .setItems(names.toArray(new String[0]), (dialog, index) -> {
                packageInput.setText(packages.get(index));
                savePackage();
                updateStatus();
            }).setNegativeButton("Cancelar", null).show();
    }

    private void launchGame() {
        savePackage();
        String pkg = packageName();
        if (pkg.isEmpty()) {
            new AlertDialog.Builder(this).setTitle("Localize o BPD Mobile")
                .setMessage("Instale o port Android original e toque em Localizar BPD Mobile instalado.")
                .setPositiveButton("Localizar", (dialog, which) -> findGame())
                .setNegativeButton("Cancelar", null).show();
            return;
        }
        Intent target = getPackageManager().getLaunchIntentForPackage(pkg);
        if (target == null) {
            new AlertDialog.Builder(this).setTitle("O jogo não está disponível")
                .setMessage("Confirme que o BPD Mobile está instalado e escolha o pacote correto. O launcher não substitui o executável do jogo.")
                .setPositiveButton("Localizar", (dialog, which) -> findGame())
                .setNegativeButton("Cancelar", null).show();
            return;
        }
        try {
            startActivity(target);
        } catch (RuntimeException e) {
            Toast.makeText(this, "Não foi possível abrir o BPD Mobile.", Toast.LENGTH_LONG).show();
        }
    }

    private void pickZip() {
        Intent picker = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        picker.addCategory(Intent.CATEGORY_OPENABLE);
        picker.setType("application/zip");
        picker.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION |
            Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        try {
            startActivityForResult(picker, PICK_ZIP);
        } catch (Exception e) {
            Toast.makeText(this, "Seletor de ZIP indisponível.", Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != PICK_ZIP || resultCode != RESULT_OK || data == null) return;
        Uri uri = data.getData();
        if (uri == null) return;
        try {
            getContentResolver().takePersistableUriPermission(
                uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
        } catch (SecurityException ignored) {
            // Permission remains transient on providers without persistable grants.
        }
        String filename = displayName(uri);
        if (!filename.toLowerCase(Locale.ROOT).endsWith(".zip")) {
            Toast.makeText(this, "Escolha um arquivo ZIP.", Toast.LENGTH_LONG).show();
            return;
        }
        prefs.edit().putString("uri", uri.toString())
            .putString("zipname", filename).apply();
        updateData();
    }

    private String displayName(Uri uri) {
        String name = "BDP_MOBILE_DATA.zip";
        try (Cursor c = getContentResolver().query(uri, null, null, null, null)) {
            if (c != null && c.moveToFirst()) {
                int idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (idx >= 0) name = c.getString(idx);
            }
        } catch (Exception ignored) {}
        return name == null ? "dados.zip" : name;
    }

    private void updateData() {
        if (dataText == null) return;
        String filename = prefs.getString("zipname", "");
        dataText.setText(filename.isEmpty() ?
            "Ainda não foi selecionado o ZIP de dados." :
            "Arquivo localizado: " + filename + "\nImporte este ZIP dentro do BPD Mobile.");
    }

    private void copyCommand(boolean reset) {
        savePackage();
        String pkg = packageName();
        if (!pkg.matches("[A-Za-z_][A-Za-z0-9_]*(\\.[A-Za-z_][A-Za-z0-9_]*)+")) {
            Toast.makeText(this, "Selecione o aplicativo BPD Mobile primeiro.", Toast.LENGTH_LONG).show();
            return;
        }
        int profile = profilePicker.getSelectedItemPosition();
        String command = reset || profile == 2 ? "adb shell cmd game reset " + pkg :
            "adb shell cmd game set --downscale " +
            (profile == 1 ? "0.8" : "0.9") + " --fps 30 " + pkg;
        copy(command);
    }

    private void copy(String value) {
        ClipboardManager clipboard = (ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("BPD Launcher", value));
            Toast.makeText(this, "Copiado.", Toast.LENGTH_SHORT).show();
        }
    }

    private String deviceInfo() {
        ActivityManager manager = (ActivityManager)getSystemService(Context.ACTIVITY_SERVICE);
        ActivityManager.MemoryInfo info = new ActivityManager.MemoryInfo();
        if (manager != null) manager.getMemoryInfo(info);
        boolean vulkan = getPackageManager().hasSystemFeature("android.hardware.vulkan.level");
        String soc = Build.VERSION.SDK_INT >= 31 ? Build.SOC_MODEL : Build.HARDWARE;
        return "Aparelho: " + Build.MANUFACTURER + " " + Build.MODEL +
            "\nAndroid: " + Build.VERSION.RELEASE +
            "\nSoC detectado: " + soc +
            "\nRAM total aproximada: " + Math.round(info.totalMem / 1073741824.0) + " GiB" +
            "\nVulkan declarado: " + (vulkan ? "Sim" : "Não detectado") +
            "\nPerfil-alvo: Dimensity 8400-Ultra / Mali-G720";
    }

    @Override protected void onResume() {
        super.onResume();
        if (packageInput != null) updateStatus();
    }

    @Override protected void onPause() {
        super.onPause();
        if (packageInput != null) savePackage();
    }
}
